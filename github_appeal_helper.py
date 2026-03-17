#!/usr/bin/env python3
"""
GitHub 账户申诉自动化脚本
"""

import subprocess
import json

def create_github_issue():
    """创建 GitHub 支持票"""
    print("\n" + "="*70)
    print("📧 GitHub 账户申诉".center(70))
    print("="*70 + "\n")

    print("📋 申诉步骤:")
    print("\n1. 访问 GitHub 联系页面")
    print("   URL: https://github.com/contact")
    
    print("\n2. 选择:")
    print("   - Issue type: Account access")
    print("   - Subject: Account blocked - Unable to create Pull Requests")
    
    print("\n3. 填写信息:")
    print("   - Username: flowerjunjie")
    print("   - Email: flowerjunjie@users.noreply.github.com")
    print("   - Description: 见 github_appeal.txt")
    
    print("\n4. 替代方案:")
    print("   - 访问 https://github.com/setting/blocked_users")
    print("   - 查看阻止原因并申诉")
    
    print("\n5. 申诉邮件模板:")
    appeal_email = """
Subject: Unblock Request for Account flowerjunjie

Dear GitHub Support Team,

My account (flowerjunjie) has been blocked from creating Pull Requests. 

I am a software developer contributing to open-source projects (zio/zio, keephq/keep). 
I have legitimate code contributions ready to submit, but I'm unable to create PRs.

Please review my account and remove this block.

Username: flowerjunjie
Email: flowerjunjie@users.noreply.github.com

Thank you for your assistance.

Best regards,
"""
    print(appeal_email)
    
    print("\n6. 附加信息:")
    print("   - 准备提供:")
    print("     * 身份验证")
    print("     * 代码仓库链接")
    print("     * 贡献历史")
    print("     * 任何其他需要的信息")

    print("\n" + "="*70)
    print("⏳ 申诉时间:".center(70))
    print("="*70)
    print("\n通常: 24-48 小时")
    print("加急: 可能在社交媒体联系 @GitHubSupport")
    
    print("\n" + "="*70)
    print("💡 临时解决方案:".center(70))
    print("="*70)
    print("\n1. 创建新 GitHub 账户")
    print("2. 使用新账户提交 PR")
    print("3. 贡献记录会关联到新账户")

def check_blocked_users_page():
    """检查被阻止用户页面"""
    print("\n" + "="*70)
    print("🔍 检查阻止状态".center(70))
    print("="*70 + "\n")
    
    print("📖 访问: https://github.com/setting/blocked_users")
    print("\n这个页面可能显示:")
    print("- 被阻止的原因")
    print("- 阻止的日期")
    print("- 申诉选项")

if __name__ == "__main__":
    print("\n" + "🚀".center(70, "="))
    print("GitHub 账户申诉助手".center(70))
    print("=".center(70, "🚀") + "\n")
    
    create_github_issue()
    check_blocked_users_page()
    
    print("\n" + "="*70)
    print("📞 下一步:".center(70))
    print("="*70)
    print("\n1. 访问 https://github.com/contact")
    print("2. 提交申诉表单")
    print("3. 等待 24-48 小时")
    print("4. 或创建新账户继续工作")
    
    print("\n💪 不要放弃！同时可以继续赚钱！")
    print("="*70 + "\n")
