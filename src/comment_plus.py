"""每日评论自动化 - 使用API直接发送评论"""
import os
import time
import random
import requests
from urllib.parse import unquote
from utils import (
    get_all_cookies,
    claim_rewards,
    get_task_list,
    extract_tasks_from_response,
    extract_user_info_from_cookies,
    claim_task_reward
)

# 配置
MAX_RETRIES = 3

# 评论内容池 (通用型支持语句)
COMMENTS = [
    "(゜∀゜*)",
    "(⁠・⁠∀⁠・⁠)",
    "(⁠ ⁠╹⁠▽⁠╹⁠ ⁠)",
    "(´・ω・｀)",
    "₍˄·͈༝·͈˄*₎◞ ̑̑",
    "(・ω・)",
    "(*╹▽╹*)",
    "(¦3[▓▓]",
]


def mask_phone(phone):
    """对手机号进行打码处理，不暴露任何数字"""
    if phone is None:
        return None
    phone_str = str(phone)
    if phone_str.strip():
        return "***"
    return phone_str


def check_user_commented(token, comic_id, uid):
    """通过评论列表API检查用户是否已在该漫画下发表过评论

    Args:
        token: 用户token
        comic_id: 漫画ID
        uid: 用户ID

    Returns:
        bool: 是否已评论过
    """
    try:
        url = "https://v4api.zaimanhua.com/app/v1/comment/list"
        headers = {
            "Authorization": f"Bearer {token}",
        }
        params = {
            "type": 4,
            "objId": comic_id,
            "sort": 1,
            "page": 0,
            "size": 30,
            "channel": "android",
            "timestamp": str(int(time.time())),
            "uid": uid,
        }
        resp = requests.get(url, headers=headers, params=params, timeout=20)
        result = resp.json()
        if result.get("errno") != 0:
            return False
        data = result.get("data", {})
        comment_list = data.get("commentList", {})
        for comment in comment_list.values():
            if comment.get("sender_uid") == uid:
                return True
        return False
    except Exception as e:
        print(f"  检查评论历史失败: {e}")
        return False


def send_comment_api(token, comic_id, content):
    """通过API直接发送评论

    Args:
        token: 用户token
        comic_id: 漫画ID
        content: 评论内容

    Returns:
        (success: bool, response: dict)
    """
    url = "https://v4api.zaimanhua.com/app/v1/comment/create"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    data = {
        "obj_id": int(comic_id),
        "to_comment_id": 0,
        "type": 4,  # 漫画类型，AppConstant.kTypeComic
        "content": content,
        "img": [],
    }
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=20)
        result = resp.json()
        if result.get("errno") == 0:
            return True, result
        else:
            return False, result
    except Exception as e:
        return False, {"errmsg": str(e)}


def post_daily_comment(cookie_str, bind_phone=None):
    """发表每日评论（API直接发送版本）

    Args:
        cookie_str: Cookie字符串
        bind_phone: 从API登录响应获取的绑定手机号（可选），如果为None则从Cookie中提取
    """
    print("\n=== 每日评论任务 ===")

    # 预检查：手机绑定状态和任务状态
    user_info = extract_user_info_from_cookies(cookie_str)
    token = user_info.get('token')
    uid = user_info.get('uid')

    # 检查任务是否已完成
    if token:
        print("检查当前任务状态...")
        task_result = get_task_list(token)
        if task_result and task_result.get('errno') == 0:
            tasks = extract_tasks_from_response(task_result)
            for task in tasks:
                task_id = task.get('id') or task.get('taskId')
                if task_id == 14:
                    if task.get('status') == 3:
                        print("  评论任务已完成，无需再次评论")
                        return True
                    break

    # 检查手机绑定：优先使用API登录返回的bind_phone
    if bind_phone is not None:
        phone_bound = bind_phone and str(bind_phone) not in ['0', '', 'None', 'False']
        print(f"使用API登录返回的手机号: bind_phone={mask_phone(bind_phone)}")
    else:
        phone_bound = user_info.get('bind_phone')
        phone_bound = phone_bound and str(phone_bound) not in ['0', '', 'None', 'False']
        print(f"从Cookie中提取的手机号: bind_phone={mask_phone(user_info.get('bind_phone'))}")

    if not phone_bound:
        print(f"警告: 检测到当前账号未绑定手机号 (bind_phone={mask_phone(bind_phone or user_info.get('bind_phone'))})")
        print("注意: 未绑定手机号的账号无法完成评论任务。为了避免工作流失败，将跳过此任务。")
        return True

    try:
        # 随机漫画尝试（失败自动换一部）
        max_comic_attempts = 10
        for comic_attempt in range(max_comic_attempts):
            comic_id = str(random.randint(4, 86783))

            print(f"随机选择漫画ID: {comic_id} (尝试 {comic_attempt + 1}/{max_comic_attempts})")
            print(f"  漫画详情页: https://m.zaimanhua.com/pages/comic/detail?id={comic_id}")

            # 检查是否已评论过该漫画
            if uid and check_user_commented(token, comic_id, uid):
                print(f"  该漫画已评论过，跳过...")
                continue

            comment_text = random.choice(COMMENTS)
            print(f"发送评论: {comment_text}")

            success, result = send_comment_api(token, comic_id, comment_text)
            if success:
                print(f"  评论发送成功！")
                return True
            else:
                errmsg = result.get('errmsg', '未知错误')
                print(f"  评论发送失败: {errmsg}")
                continue

        # 所有漫画尝试均失败
        print("多次随机漫画尝试后仍失败")
        return False

    except Exception as e:
        print(f"评论任务失败: {e}")
        return False


def check_comment_task_status(token):
    """检查评论任务（每日一评）状态

    返回:
        - status: 1=未完成, 2=可领取, 3=已完成
        - task_id: 任务ID
    """
    try:
        task_result = get_task_list(token)
        if task_result and task_result.get('errno') == 0:
            tasks = extract_tasks_from_response(task_result)
            for task in tasks:
                task_id = task.get('id') or task.get('taskId')
                task_name = task.get('title') or task.get('name') or task.get('taskName', '')
                is_comment_task = (task_id == 14 or
                                 '评论' in str(task_name) or
                                 '一评' in str(task_name))
                if is_comment_task:
                    status = task.get('status', 0)
                    print(f"  评论任务状态: ID={task_id}, 名称={task_name}, status={status}")
                    return status, task_id
        return None, None
    except Exception as e:
        print(f"  检查任务状态异常: {e}")
        return None, None


def run_comment(cookie_str, bind_phone=None):
    """执行评论任务（API直接发送版本）

    Args:
        cookie_str: Cookie字符串
        bind_phone: 从API登录响应获取的绑定手机号（可选）
    """
    try:
        # 发表评论
        comment_result = post_daily_comment(cookie_str, bind_phone=bind_phone)

        # 领取积分
        claim_result = claim_rewards(None, cookie_str)

        # 检查评论任务是否真正完成（status=2或3）
        user_info = extract_user_info_from_cookies(cookie_str)
        token = user_info.get('token') if isinstance(user_info, dict) else None

        if token and comment_result:
            print("\n=== 验证评论任务状态 ===")
            max_verify_retries = 3
            for verify_attempt in range(max_verify_retries):
                status, task_id = check_comment_task_status(token)

                if status == 3:
                    print(f"  [v] 评论任务已完成并领取 (status=3)")
                    break
                elif status == 2:
                    print(f"  [v] 评论任务已完成，尝试领取奖励...")
                    success, result = claim_task_reward(token, task_id)
                    if success:
                        print(f"  [OK] 奖励领取成功！")
                    break
                elif status == 1:
                    if verify_attempt < max_verify_retries - 1:
                        print(f"  [!] 评论任务未完成 (status=1)，可能评论未发送成功，准备重新评论...")
                        # 重新发表评论
                        comment_result = post_daily_comment(cookie_str)
                        if comment_result:
                            print(f"  [v] 重新评论完成，等待服务器同步...")
                            time.sleep(5)
                        else:
                            print(f"  [x] 重新评论失败")
                            break
                    else:
                        print(f"  [x] 评论任务仍未完成，已达到最大重试次数")
                        comment_result = False
                else:
                    print(f"  [?] 无法获取评论任务状态，跳过验证")
                    break

        return {
            'comment': comment_result,
            'claim': claim_result
        }

    except Exception as e:
        print(f"任务执行出错: {e}")
        return {'comment': False, 'claim': False}


def main():
    """主函数，支持多账号"""
    cookies_list = get_all_cookies()

    if not cookies_list:
        print("Error: 未配置任何账号 Cookie")
        print("请设置 ZAIMANHUA_COOKIE 或 ZAIMANHUA_COOKIE_1 等环境变量")
        return False

    print(f"共发现 {len(cookies_list)} 个账号")

    all_success = True
    for index, (name, cookie_str) in enumerate(cookies_list):
        print(f"\n{'='*50}")
        print(f"正在执行评论任务: {name}")
        print('='*50)

        # 验证 Cookie 有效性，如果失效尝试自动登录
        # 使用对应的账号索引获取对应的多账号凭据
        from auto_login import get_valid_cookie
        valid_cookie, is_auto_login = get_valid_cookie(cookie_str, name, account_index=index if index > 0 else None)

        if not valid_cookie:
            print(f"[ERROR] 无法获取有效Cookie")
            all_success = False
            continue

        if is_auto_login:
            print(f"  [v] 使用自动登录获取的新Cookie")
            cookie_str = valid_cookie
        else:
            print(f"  [v] 使用配置的Cookie")

        # 从Cookie中提取bind_phone用于评论任务验证
        bind_phone = None
        user_info = extract_user_info_from_cookies(cookie_str)
        if isinstance(user_info, dict):
            bind_phone = user_info.get('bind_phone')
            if bind_phone:
                print(f"  [v] 获取到绑定手机号: {mask_phone(bind_phone)}")
            else:
                print(f"  [!] 未获取到绑定手机号")

        for attempt in range(1, MAX_RETRIES + 1):
            print(f"\n尝试第 {attempt}/{MAX_RETRIES} 次...")
            try:
                results = run_comment(cookie_str, bind_phone=bind_phone)

                if results.get('comment') is False:
                    if attempt < MAX_RETRIES:
                        print(f"评论失败，等待重试...")
                        time.sleep(10)
                        continue
                    else:
                        all_success = False
                break

            except Exception as e:
                print(f"第 {attempt} 次尝试出错: {e}")
                if attempt < MAX_RETRIES:
                    time.sleep(10)
                else:
                    all_success = False

    print(f"\n{'='*50}")
    if all_success:
        print("所有账号评论任务完成！")
    else:
        print("部分任务失败，请检查日志")

    return all_success


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
