"""
创建飞书多维表格结构
"""

import sys
from pathlib import Path

# 添加scraper目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from feishu_client import FeishuClient


# 表格和字段配置
TABLES_CONFIG = {
    "recalled_batches": {
        "name": "召回批次",
        "description": "记录所有召回批次信息",
        "fields": [
            {
                "field_name": "brand",
                "type": 1,  # text
                "description": "品牌（雀巢、Abbott等）",
            },
            {"field_name": "brand_en", "type": 1, "description": "品牌英文名"},
            {"field_name": "product_name", "type": 1, "description": "产品名称"},
            {"field_name": "sub_brand", "type": 1, "description": "子品牌（SMA、NAN）"},
            {
                "field_name": "batch_codes",
                "type": 17,  # text（多值）
                "description": "批次号列表（逗号分隔）",
            },
            {
                "field_name": "pack_size",
                "type": 1,
                "description": "包装规格（800g、400g）",
            },
            {
                "field_name": "best_before",
                "type": 5,  # date
                "description": "有效期",
            },
            {
                "field_name": "region",
                "type": 17,
                "description": "受影响地区（UK/US/EU/China）",
            },
            {"field_name": "recall_reason", "type": 1, "description": "召回原因"},
            {
                "field_name": "risk_level",
                "type": 4,  # singleSelect
                "description": "风险等级",
                "property": {
                    "options": [{"name": "高"}, {"name": "中"}, {"name": "低"}]
                },
            },
            {
                "field_name": "source_url",
                "type": 15,  # url
                "description": "官方来源链接",
            },
            {
                "field_name": "source_type",
                "type": 4,
                "description": "数据源类型",
                "property": {
                    "options": [
                        {"name": "官网"},
                        {"name": "政府平台"},
                        {"name": "社交媒体"},
                    ]
                },
            },
            {"field_name": "published_date", "type": 5, "description": "发布日期"},
            {"field_name": "last_updated", "type": 5, "description": "最后更新日期"},
            {
                "field_name": "status",
                "type": 4,
                "description": "状态",
                "property": {
                    "options": [
                        {"name": "召回中"},
                        {"name": "已结束"},
                        {"name": "待确认"},
                    ]
                },
            },
        ],
    },
    "brand_config": {
        "name": "品牌配置",
        "description": "品牌配置信息",
        "fields": [
            {"field_name": "brand_name", "type": 1, "description": "品牌名称"},
            {"field_name": "brand_name_en", "type": 1, "description": "品牌英文名称"},
            {"field_name": "sub_brands", "type": 17, "description": "子品牌列表"},
            {
                "field_name": "batch_pattern",
                "type": 1,
                "description": "批次号格式模式（正则）",
            },
            {"field_name": "data_sources", "type": 17, "description": "数据源列表"},
            {
                "field_name": "last_scrape_date",
                "type": 5,
                "description": "最后爬取日期",
            },
            {
                "field_name": "active",
                "type": 9,  # checkbox
                "description": "是否激活",
            },
        ],
    },
    "query_logs": {
        "name": "查询日志",
        "description": "查询日志记录",
        "fields": [
            {
                "field_name": "query_text",
                "type": 1,
                "description": "查询内容（OCR或手动输入）",
            },
            {
                "field_name": "match_result",
                "type": 4,
                "description": "匹配结果",
                "property": {
                    "options": [
                        {"name": "召回"},
                        {"name": "未召回"},
                        {"name": "未找到"},
                    ]
                },
            },
            {
                "field_name": "query_method",
                "type": 4,
                "description": "查询方式",
                "property": {"options": [{"name": "OCR"}, {"name": "手动"}]},
            },
            {"field_name": "query_date", "type": 5, "description": "查询时间"},
        ],
    },
}


class FeishuTableManager:
    """飞书表格管理器"""

    def __init__(self, client: FeishuClient, app_token: str):
        self.client = client
        self.app_token = app_token
        self.table_ids = {}

    def create_all_tables(self):
        """创建所有表格"""
        print("=" * 60)
        print("开始创建飞书多维表格结构")
        print("=" * 60)

        for table_key, config in TABLES_CONFIG.items():
            print(f"\n创建表格: {config['name']}")
            try:
                table_id = self.create_table(config)
                self.table_ids[table_key] = table_id
                print(f"  ✅ 表格创建成功")
                print(f"     Table ID: {table_id}")
            except Exception as e:
                print(f"  ❌ 创建失败: {e}")

        return self.table_ids

    def create_table(self, config: dict) -> str:
        """
        创建表格

        Returns:
            table_id: 表格ID
        """
        # 创建表格
        table_data = {
            "table": {"name": config["name"], "default_view_name": "默认视图"}
        }

        result = self.client._make_request(
            "POST", f"/bitable/v1/apps/{self.app_token}/tables", table_data
        )

        table_id = result["table"]["table_id"]
        print(f"  - 表格ID: {table_id}")

        # 添加字段
        print(f"  - 添加字段...")
        for field_config in config["fields"]:
            self.create_field(table_id, field_config)

        return table_id

    def create_field(self, table_id: str, field_config: dict):
        """创建字段"""
        field_data = {
            "field_name": field_config["field_name"],
            "type": field_config["type"],
            "description": field_config["description"],
        }

        # 添加可选属性（如单选选项）
        if "property" in field_config:
            field_data["property"] = field_config["property"]

        try:
            result = self.client._make_request(
                "POST",
                f"/bitable/v1/apps/{self.app_token}/tables/{table_id}/fields",
                field_data,
            )
            print(
                f"    ✅ {field_config['field_name']}: {field_config.get('description', '')}"
            )
        except Exception as e:
            print(f"    ⚠️  {field_config['field_name']}: {e}")


def main():
    """主函数"""
    # 飞书凭证
    app_id = "cli_a9f1f4887e38dcd2"
    app_secret = "aNhAQdFTDJSWaQZnj2dy7dXvDgOzdi7u"

    # 从URL解析app_token
    app_token = "Af9TwoIEkiJwkhkq0YEcw3WRnMZ"

    # 创建客户端
    client = FeishuClient(app_id, app_secret)

    # 创建表格管理器
    manager = FeishuTableManager(client, app_token)

    # 创建所有表格
    try:
        table_ids = manager.create_all_tables()

        print("\n" + "=" * 60)
        print("✅ 所有表格创建成功！")
        print("=" * 60)
        print(f"\n表格ID映射:")
        for key, table_id in table_ids.items():
            print(f"  {key}: {table_id}")

        # 保存配置
        config_text = f"""
# 飞书表格配置
APP_TOKEN = "{app_token}"

TABLE_IDS = {{
    "recalled_batches": "{table_ids.get("recalled_batches", "")}",
    "brand_config": "{table_ids.get("brand_config", "")}",
    "query_logs": "{table_ids.get("query_logs", "")}"
}}
"""
        with open(
            "/Users/jiang/clawd/recall-checker/scraper/utils/feishu_config.py",
            "w",
            encoding="utf-8",
        ) as f:
            f.write(config_text)

        print("\n配置已保存到: scraper/utils/feishu_config.py")

    except Exception as e:
        print(f"\n❌ 创建失败: {e}")


if __name__ == "__main__":
    main()
