# 遊漁船 釣果データ収集プロジェクト

日本全国の遊漁船（船宿）について「いま・どこで・何が・どれぐらい釣れているか」を
一覧できるデータベースとWebサイトを構築するプロジェクト。まず神奈川県から。

## データ資産

| パス | 役割 |
|---|---|
| `data/boats.json` | データの正（source of truth） |
| `data/master_kanagawa.xlsx` | 人間閲覧用マスター台帳（boats.json から生成） |
| `site/index.html` | 閲覧サイト（boats.json 埋め込みの単一HTML） |
| `logs/progress.md` | バッチごとの進捗ログ |

## スクリプト

```bash
python3 scripts/json_to_xlsx.py   # boats.json → data/master_kanagawa.xlsx
python3 scripts/build_site.py    # boats.json → site/index.html
python3 scripts/make_master.py   # 初期マスターの再生成（既存データを上書きするので注意）
```

依存: `pip install openpyxl`

## boats.json スキーマ

```json
{
  "no": 1,
  "pref": "神奈川県",
  "city": "川崎市",
  "port": "川崎",
  "name": "中山丸",
  "url": "https://www.nakayamamaru.com/",
  "type": "乗合",
  "catches": [
    {"fish": "アナゴ", "size": "28〜48cm", "count": "1〜30本",
     "note": "船中155本", "date": "2026-07-03"}
  ],
  "prices": [
    {"label": "ショートLTアジ", "yen": 8800, "note": "燃油サーチャージ+500円"}
  ],
  "status": "済",
  "source": "公式サイト",
  "collected_at": "2026-07-04",
  "error_count": 0
}
```

- `type`: 乗合 | チャーター | 仕立中心 | 不明
- `status`: 未収集 | 済 | 一部 | 取得不可
- `source`: 公式サイト | 釣りビジョン | 釣割 | つりー | その他
- `date` は釣果の日付（収集日と混同しない）
- `yen` が取れないときは推測で埋めない

## 収集ルール（要約）

- status=未収集 の船を No. 順に処理。20隻ごとに保存＋進捗ログ、50隻ごとに Excel/サイト再生成
- 品質基準: 魚種・サイズ・数・日付のうちサイズ/数/日付の2つ以上が揃って「済」。
  揃わなければ取れた範囲で「一部」
- チャーター・仕立専門など日次乗合釣果を出さない業態は type 変更＋note 記録で「一部」
- アクセス不能は error_count++、3回失敗で「取得不可」

## 既知の制約（この実行環境）

- 実行環境の egress ポリシーにより、船宿公式サイト・funaduri.jp・釣りビジョン等への
  **直接HTTPアクセスは全てブロック**されている（プロキシが403を返す）
- 利用可能な収集手段は WebSearch（検索API経由）のみ。よって:
  - マスターは funaduri.jp の県別ページからではなく、港別のWeb検索で構築した
    （このため現状 285 隻ではなく検索で確認できた範囲の隻数）
  - 釣果・料金は検索結果スニペットから取れた範囲で記録し、精度が担保できない値は
    記録しない方針
- ネットワークポリシーを緩和（対象ドメイン許可）すれば、仕様書どおりの
  直接クロールパイプラインに移行できる
