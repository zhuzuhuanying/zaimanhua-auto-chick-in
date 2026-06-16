"""每日综合任务脚本 - 签到 + 评论 + 阅读，一次登录完成所有日常任务"""
import time
from auto_login import get_valid_cookie
from utils import (
    get_all_cookies,
    extract_user_info_from_cookies,
    claim_task_reward,
    get_task_list,
    extract_tasks_from_response,
)
from checkin import checkin, claim_checkin_reward, claim_vip_reward
from comment_plus import run_comment
from auto_read import ZaimanhuaAppReader, try_ui_claim

# 配置
READ_TASK_ID = 13  # 海螺小姐 (阅读10分钟)
MAX_READ_MINUTES = 30


def claim_all_pending_rewards(cookie_str):
    """通过 API 领取所有可领取的任务奖励"""
    print("\n--- 统一领取所有可领取奖励 ---")
    user_info = extract_user_info_from_cookies(cookie_str)
    token = user_info.get('token') if isinstance(user_info, dict) else None
    if not token:
        print("  无法获取 token，跳过统一领取")
        return False

    task_result = get_task_list(token)
    if not task_result or task_result.get('errno') != 0:
        print("  获取任务列表失败")
        return False

    tasks = extract_tasks_from_response(task_result)
    claimed = 0
    failed = 0
    for task in tasks:
        task_id = task.get('id') or task.get('taskId')
        task_name = task.get('title') or task.get('name') or task.get('taskName', '未知')
        status = task.get('status', 0)
        if status == 2 and task_id:
            print(f"  领取任务: {task_name} (ID: {task_id})")
            success, result = claim_task_reward(token, task_id)
            if success:
                print(f"    [OK] 领取成功")
                claimed += 1
            else:
                print(f"    [FAIL] 领取失败")
                failed += 1

    if claimed == 0 and failed == 0:
        print("  没有可领取的奖励")
    else:
        print(f"  领取完成: 成功 {claimed} 个, 失败 {failed} 个")
    return failed == 0


def run_read_task(cookie_str):
    """执行阅读/观看任务"""
    print("\n=== 每日阅读任务 ===")
    reader = ZaimanhuaAppReader(cookie_str, debug=False)
    token = reader.get_token()
    if not token:
        print("  Token 无效，跳过阅读任务")
        return False

    status = reader.get_task_status(READ_TASK_ID)

    # 已完成
    if status == 3:
        print("  阅读任务已完成 (status=3)")
        return True

    # 可领取
    if status == 2:
        print("  阅读任务可领取 (status=2)，尝试领取...")
        success, res = claim_task_reward(token, READ_TASK_ID)
        if success:
            print("  [OK] API 领取成功")
            return True
        print("  API 领取失败，尝试 UI 领取...")
        if try_ui_claim(cookie_str):
            print("  [OK] UI 领取成功")
            return True
        print("  [FAIL] UI 领取也失败")
        return False

    # 未完成，开始阅读
    if status is None:
        print("  无法确定阅读任务状态，跳过")
        return False

    print(f"  阅读任务未完成 (status={status})，开始阅读...")
    for m in range(1, MAX_READ_MINUTES + 1):
        print(f"\n  --- 第 {m}/{MAX_READ_MINUTES} 分钟 ---")
        reader.simulate_reading(minutes=1)

        new_status = reader.get_task_status(READ_TASK_ID)
        if new_status == 3:
            print("  [OK] 阅读任务已完成 (status=3)")
            return True
        if new_status == 2:
            print("  [OK] 阅读任务可领取 (status=2)，尝试领取...")
            success, res = claim_task_reward(token, READ_TASK_ID)
            if success:
                print("  [OK] API 领取成功")
                return True
            print("  API 领取失败，尝试 UI 领取...")
            if try_ui_claim(cookie_str):
                print("  [OK] UI 领取成功")
                return True
            print("  [FAIL] 领取失败，继续阅读...")

        if m == MAX_READ_MINUTES:
            print(f"  [FAIL] 已达到最大阅读时长 {MAX_READ_MINUTES} 分钟，任务仍未完成")
            return False

    return False


def run_account_daily_tasks(index, name, cookie_str):
    """为单个账号执行所有日常任务"""
    print(f"\n{'='*60}")
    print(f"账号: {name}")
    print(f"{'='*60}")

    # 1. 验证 Cookie / 自动登录（只做一次）
    valid_cookie, is_auto_login = get_valid_cookie(
        cookie_str, name, account_index=index if index > 0 else None
    )
    if not valid_cookie:
        print("[ERROR] 无法获取有效 Cookie")
        return False

    if is_auto_login:
        print("  [v] 使用自动登录获取的新 Cookie")
        cookie_str = valid_cookie
    else:
        print("  [v] 使用配置的 Cookie")

    all_ok = True

    # 2. 签到任务
    print("\n" + "="*60)
    print("开始执行: 签到任务")
    print("="*60)
    try:
        success = checkin(cookie_str)
        if success:
            claim_checkin_reward(cookie_str)
            claim_vip_reward(cookie_str)
        else:
            all_ok = False
    except Exception as e:
        print(f"  签到任务异常: {e}")
        all_ok = False

    # 3. 评论任务
    print("\n" + "="*60)
    print("开始执行: 评论任务")
    print("="*60)
    try:
        user_info = extract_user_info_from_cookies(cookie_str)
        bind_phone = user_info.get('bind_phone') if isinstance(user_info, dict) else None
        results = run_comment(cookie_str, bind_phone=bind_phone)
        if not results.get('comment'):
            all_ok = False
    except Exception as e:
        print(f"  评论任务异常: {e}")
        all_ok = False

    # 4. 阅读任务
    print("\n" + "="*60)
    print("开始执行: 阅读任务")
    print("="*60)
    try:
        if not run_read_task(cookie_str):
            all_ok = False
    except Exception as e:
        print(f"  阅读任务异常: {e}")
        all_ok = False

    # 5. 统一领取所有可领取的奖励（兜底）
    try:
        claim_all_pending_rewards(cookie_str)
    except Exception as e:
        print(f"  统一领取奖励异常: {e}")

    return all_ok


def main():
    """主函数，支持多账号"""
    cookies_list = get_all_cookies()
    if not cookies_list:
        print("Error: 未配置任何账号 Cookie")
        print("请设置 ZAIMANHUA_COOKIE 或 ZAIMANHUA_USERNAME/ZAIMANHUA_PASSWORD 环境变量")
        return False

    print(f"共发现 {len(cookies_list)} 个账号")

    all_success = True
    for index, (name, cookie_str) in enumerate(cookies_list):
        ok = run_account_daily_tasks(index, name, cookie_str)
        if not ok:
            all_success = False
        # 账号之间稍作间隔，避免请求过快
        if index < len(cookies_list) - 1:
            print("\n等待 5 秒后切换下一个账号...")
            time.sleep(5)

    print(f"\n{'='*60}")
    if all_success:
        print("所有账号日常任务执行完成！")
    else:
        print("部分账号任务失败，请检查日志")
    print("="*60)
    return all_success


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
