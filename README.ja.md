# service-research

製品・サービスを調査し — 概要・料金・利用規約・プライバシーポリシー・データ
セキュリティ・AI エージェント動作 — スキーマ検証済みの JSON レポート
（3 段階リスク評価付き）と Markdown レポートを生成する Claude Code Skill。
`/service-research <名前>` で起動します。

アーカイブ済み [product-research](https://github.com/nlink-jp/product-research)
CLI の後継です。CLI は調査を検索グラウンディング付き Gemini の単発呼び出しに
委ねており、利用規約やプライバシーポリシーのページを実際に開くことは一度も
なく、sources はグラウンディングメタデータの申告のままでした。本スキルは
エージェント自身が調査します — 複数回の検索、ポリシーページ原文の取得と読解、
既知インシデントの独立した検索 — そして `sources` には実際に読んだ URL のみが
載ります。JSON 構造は CLI と同一で、新旧レポートは直接比較できます。
GCP プロジェクト・ADC・Vertex AI コストは不要になりました。
（設計: [ADR-0001](docs/ja/adr/0001-agentic-research.ja.md)）

## インストール

リリース zip から（claude.ai → Settings → Skills にそのままアップロードも可）:

```bash
unzip service-research-vX.Y.Z.zip -d ~/.claude/skills/
```

チェックアウトから:

```bash
make install
```

必要要件: Web アクセス（WebSearch/WebFetch）が有効な Claude Code、および同梱
スクリプト用の `python3`（3.9+、stdlib のみ）。

## 使い方

```
/service-research Slack
/service-research "GitHub Copilot" --lang en
```

スコープ確定 → セクション別調査 → リスク統合 → 検証 → コンパイル の
ワークフローを経て `./reports/` に生成します:

- `<名前>_<日付>.json` — 構造化レポート（スキーマ:
  `service-research/schema.json`、意味論:
  `service-research/references/report-format.md`）
- `<名前>_<日付>.md` — 人間向けレポート

レポートはデフォルト日本語。`--lang en` で全フィールド・ラベルが英語に
なります。見つからなかった情報は `不明` / `unknown` — 推測はしません。

旧 CLI のレポートはそのまま再コンパイルできます:

```bash
python3 ~/.claude/skills/service-research/scripts/compile.py old-report.json -o old-report.md
```

## 開発

| コマンド | 用途 |
|---------|------|
| `make check`（= `make test`） | 構造検証 + スクリプト挙動テスト |
| `make install` | `~/.claude/skills/service-research` へコピー |
| `make package` | `dist/service-research-vX.Y.Z.zip` を作成（zip ルート = スキルフォルダ） |

## ドキュメント

- [レポートフォーマット仕様](service-research/references/report-format.md)
- [ADR-0001 — 設計決定記録](docs/ja/adr/0001-agentic-research.ja.md)
- [English documentation](README.md)

## 注意

- 調査結果は調査時点の公開 Web 情報に基づきます。規約・ポリシーは変わるため、
  公式ページが常に正です。
- 調査中にサインアップ・ログイン・ダウンロード・実行は一切行わず、取得した
  ページ内容はすべて信頼できないデータとして扱います。

## ライセンス

MIT
