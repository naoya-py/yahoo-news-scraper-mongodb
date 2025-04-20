import os
from datetime import datetime

class SelectorUtils:
    """
    セレクタのフォールバック取得や、HTMLスナップショット保存など
    セレクタ耐障害性・保守性を向上させるユーティリティクラス
    """

    def __init__(self, snapshot_dir="debug_snapshots", logger=None):
        self.snapshot_dir = snapshot_dir
        self.logger = logger

    def try_multiple_selectors(self, page, selectors):
        """
        複数のセレクタ候補を順に試し、最初に見つかった要素を返す。
        """
        for selector in selectors:
            el = page.locator(selector).first
            if el and el.is_visible():
                return el
        return None

    def save_html_snapshot(self, page, url, prefix="snapshot"):
        """
        セレクタ取得失敗時にHTMLスナップショットを保存する
        """
        try:
            html = page.content()
            safe_url = (
                url.replace("https://", "")
                .replace("http://", "")
                .replace("/", "_")
                .replace("?", "_")
                .replace(":", "_")
            )
            fname = f"{prefix}_{safe_url}_{datetime.now().strftime('%Y%m%d%H%M%S')}.html"
            os.makedirs(self.snapshot_dir, exist_ok=True)
            path = os.path.join(self.snapshot_dir, fname)
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            if self.logger:
                self.logger.info(f"HTMLスナップショット保存: {path}")
            return path
        except Exception as e:
            if self.logger:
                self.logger.error(f"HTMLスナップショット保存失敗: {e}")
            return None