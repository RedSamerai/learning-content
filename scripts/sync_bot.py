#!/usr/bin/env python3
"""
SyncBot - 同步Bot
管理内容与学习机之间的同步
"""

import asyncio
import aiohttp
import json
import hashlib
from pathlib import Path
from datetime import datetime

class SyncBot:
    """同步Bot - 管理与GitHub的知识库同步"""
    
    def __init__(self, repo_url: str = "https://github.com/RedSamerai/learning-content"):
        self.repo_url = repo_url
        self.api_url = "https://api.github.com"
        self.local_cache_dir = Path("cache")
        self.local_cache_dir.mkdir(exist_ok=True)
    
    async def check_for_updates(self) -> dict:
        """检查是否有新内容更新"""
        
        # 获取GitHub最新commit
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_url}/repos/RedSamerai/learning-content/commits/main"
            ) as response:
                if response.status == 200:
                    commit_data = await response.json()
                    return {
                        "has_update": True,
                        "commit_sha": commit_data['sha'],
                        "commit_message": commit_data['commit']['message'],
                        "committed_at": commit_data['commit']['committer']['date']
                    }
                else:
                    return {"has_update": False, "error": f"HTTP {response.status}"}
    
    async def download_content(self, topic_id: str) -> dict:
        """下载单个知识点内容"""
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_url}/repos/RedSamerai/learning-content/contents/kindergarten/math/{topic_id}.json"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    # 解码base64内容
                    import base64
                    content = base64.b64decode(data['content']).decode('utf-8')
                    return json.loads(content)
                else:
                    return None
    
    async def save_to_local(self, topic_id: str, content: dict):
        """保存到本地缓存"""
        
        cache_path = self.local_cache_dir / f"{topic_id}.json"
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 计算内容hash
        content_hash = hashlib.sha256(json.dumps(content, ensure_ascii=False).encode()).hexdigest()[:16]
        
        # 保存时附带元数据
        cache_data = {
            "content": content,
            "cached_at": datetime.now().isoformat(),
            "content_hash": content_hash
        }
        
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        return cache_path
    
    async def sync_all(self):
        """同步所有内容"""
        
        print("🔄 检查更新...")
        update_info = await self.check_for_updates()
        
        if not update_info.get('has_update'):
            print("✅ 内容已是最新")
            return
        
        print(f"📦 发现新更新: {update_info['commit_message']}")
        
        # 这里可以添加批量下载逻辑
        # 暂时只下载示例知识点
        await self.download_and_save("number_recognition")
    
    async def download_and_save(self, topic_id: str):
        """下载并保存单个知识点"""
        
        print(f"📥 下载: {topic_id}")
        content = await self.download_content(topic_id)
        
        if content:
            path = await self.save_to_local(topic_id, content)
            print(f"✅ 已保存到: {path}")
        else:
            print(f"❌ 下载失败: {topic_id}")


async def main():
    """主函数"""
    bot = SyncBot()
    await bot.sync_all()


if __name__ == '__main__':
    asyncio.run(main())
