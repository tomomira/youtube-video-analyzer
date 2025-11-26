#!/usr/bin/env python3
"""
YouTube Data API v3 動作確認スクリプト

このスクリプトは以下を確認します：
1. APIキーが正しく設定されているか
2. YouTube APIに接続できるか
3. 動画情報を取得できるか
4. ショート動画の識別方法
"""

import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import isodate

# 環境変数を読み込む
load_dotenv()

# APIキーを取得
API_KEY = os.getenv('YOUTUBE_API_KEY')

def check_api_key():
    """APIキーが設定されているか確認"""
    print("=" * 60)
    print("1. APIキーの確認")
    print("=" * 60)

    if not API_KEY:
        print("❌ エラー: YOUTUBE_API_KEYが設定されていません")
        print("   .envファイルを確認してください")
        return False

    if API_KEY == "YOUR_API_KEY_HERE":
        print("❌ エラー: APIキーが設定されていません")
        print("   .envファイルに実際のAPIキーを設定してください")
        return False

    print(f"✅ APIキーが設定されています: {API_KEY[:10]}...")
    return True

def test_youtube_connection():
    """YouTube APIに接続できるか確認"""
    print("\n" + "=" * 60)
    print("2. YouTube API接続テスト")
    print("=" * 60)

    try:
        # YouTube APIクライアントを作成
        youtube = build('youtube', 'v3', developerKey=API_KEY)
        print("✅ YouTube APIクライアントを作成しました")
        return youtube
    except Exception as e:
        print(f"❌ エラー: {e}")
        return None

def test_search_videos(youtube):
    """動画検索をテスト"""
    print("\n" + "=" * 60)
    print("3. 動画検索テスト")
    print("=" * 60)
    print("検索キーワード: 'python tutorial'")
    print("最大取得件数: 5件")

    try:
        # 動画を検索
        request = youtube.search().list(
            part='id',
            q='python tutorial',
            type='video',
            maxResults=5,
            order='viewCount'
        )

        response = request.execute()

        # 動画IDを取得
        video_ids = [item['id']['videoId'] for item in response.get('items', [])]

        print(f"✅ {len(video_ids)}件の動画を取得しました")
        print(f"   動画ID: {', '.join(video_ids[:3])}...")

        return video_ids
    except HttpError as e:
        print(f"❌ API呼び出しエラー: {e}")
        if e.resp.status == 403:
            print("   → APIキーが無効、またはAPIが有効化されていません")
            print("   → YouTube Data API v3が有効化されているか確認してください")
        return []
    except Exception as e:
        print(f"❌ エラー: {e}")
        return []

def test_get_video_details(youtube, video_ids):
    """動画の詳細情報を取得してショート動画を識別"""
    print("\n" + "=" * 60)
    print("4. 動画詳細情報取得テスト & ショート動画識別")
    print("=" * 60)

    if not video_ids:
        print("❌ 取得する動画IDがありません")
        return

    try:
        # 動画の詳細情報を取得
        request = youtube.videos().list(
            part='snippet,statistics,contentDetails',
            id=','.join(video_ids[:3])  # 最初の3件をテスト
        )

        response = request.execute()

        print(f"✅ {len(response.get('items', []))}件の詳細情報を取得しました\n")

        # ショート動画の識別方法を調査
        print("【ショート動画の識別方法の調査結果】")
        print("-" * 60)

        for item in response.get('items', []):
            snippet = item['snippet']
            statistics = item['statistics']
            content_details = item['contentDetails']

            # ISO 8601形式のdurationを秒に変換
            duration_str = content_details['duration']
            duration = int(isodate.parse_duration(duration_str).total_seconds())

            # ショート動画の判定（60秒以下）
            is_short = duration <= 60

            print(f"\n動画: {snippet['title'][:50]}...")
            print(f"  - 動画ID: {item['id']}")
            print(f"  - 再生回数: {int(statistics.get('viewCount', 0)):,}回")
            print(f"  - 公開日: {snippet['publishedAt'][:10]}")
            print(f"  - 動画の長さ: {duration}秒 ({duration // 60}分{duration % 60}秒)")
            print(f"  - ISO 8601形式: {duration_str}")
            print(f"  - ショート動画: {'✅ はい' if is_short else '❌ いいえ'}")

        print("\n" + "-" * 60)
        print("【結論】")
        print("ショート動画の識別方法:")
        print("  1. videos.listで contentDetails.duration を取得")
        print("  2. ISO 8601形式（例: PT1M30S）をパース")
        print("  3. 60秒以下かどうかで判定")
        print("  ※ YouTube APIには現時点でショート動画専用のフラグは存在しません")

    except HttpError as e:
        print(f"❌ API呼び出しエラー: {e}")
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

def main():
    """メイン関数"""
    print("\n")
    print("*" * 60)
    print("  YouTube Data API v3 動作確認スクリプト")
    print("*" * 60)

    # 1. APIキーの確認
    if not check_api_key():
        return

    # 2. YouTube API接続テスト
    youtube = test_youtube_connection()
    if not youtube:
        return

    # 3. 動画検索テスト
    video_ids = test_search_videos(youtube)

    # 4. 動画詳細情報取得テスト & ショート動画識別
    if video_ids:
        test_get_video_details(youtube, video_ids)

    # 完了メッセージ
    print("\n" + "=" * 60)
    print("✅ 全てのテストが完了しました！")
    print("=" * 60)
    print("\n次のステップ:")
    print("  1. Phase 1の実装開始")
    print("  2. データモデルの実装")
    print("  3. YouTube APIクライアントクラスの実装")
    print("\n")

if __name__ == "__main__":
    main()
