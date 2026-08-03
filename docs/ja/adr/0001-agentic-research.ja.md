# ADR-0001: service-research Skill — product-research CLI を廃止しエージェンティックリサーチへ

| 項目 | 内容 |
|------|------|
| Status | **Accepted** |
| Date | 2026-07-31 |
| Decision makers | nlink-jp maintainers |
| Triggered by | product-research の「自律 Web リサーチ」が grounding 付き Gemini 1 回呼び出しに過ぎなかったこと、およびハードコードされた `gemini-2.5-pro` が ADR-001 の移行リストに載っていたこと |

> もとは `nlink-jp/.github` の組織 ADR-007 として記録していた。
> 2026-08-03 にここへ移設。組織の ADR ログは組織全体を拘束する決定のための
> ものであり、この決定が設計するのは 1 つのスキルだけである。
> `product-research` の廃止という事実は、組織ログ側のリダイレクトエントリに
> 引き続き記録されている。

## Context

`product-research`（cybersecurity-series、Python）は製品やサービスを調査し —
概要・利用規約・プライバシー慣行・データセキュリティ・AI エージェント挙動 —
構造化レポート（Markdown + 三段階リスク評価付き JSON）を出力する。
約 480 行を分解すると:

| 部分 | 行数（概算） | 性質 |
|---|---|---|
| システムプロンプト 2 本（リサーチ 8 観点 + 抽出ルール） | ~50 | 本体そのもの |
| Pydantic スキーマ（7 モデル・約 50 フィールド） | ~100 | 本体そのもの |
| Markdown レポート整形 | ~40 | 本体そのもの |
| genai クライアント・ストリーミング・429 リトライ/バックオフ・argparse・ファイル保存・進捗 UI | ~290 | Claude Code セッションがネイティブに提供する配管 |

いま見直す動機は 2 つ:

1. **リサーチフェーズが自分の README を下回っている。**「自律 Web リサーチ」の
   実装は Google Search Grounding 付きの `generate_content` **1 回**である。
   何も反復せず、欠落を追跡もせず、システムプロンプトが「公式文書を直接
   確認せよ」と指示しているにもかかわらず、ToS やプライバシーポリシーの
   ページを一度も開かない。`sources` リストは grounding メタデータの主張で
   あって、実際に読んだページではない。
2. **ADR-001 の被弾リストに載っている。**`gemini-2.5-pro` が（当時は意図的に）
   ハードコードされており、Gemini 2.5 廃止時（2026-10-16 以降）にコード変更が
   必要な 5 リポジトリの 1 つになっている。不要な配管に移行工数を割くのは
   無駄である。

この転換にはちょうど 1 件の組織内前例がある: `meeting-note`（CLI、単発
Gemini 生成）→ `meeting-notes`（Skill、フラグメント単位の検証とリトライを
持つエージェンティックループ）、2026-07-31 完了。

## Decision

**Claude Code Skill `service-research` を `skills-series` に 1 つ追加し、
Skill が v0.1.0 を出荷した時点で `product-research` CLI をアーカイブする。**

形を決めるサブ決定は 4 つ。

### 1. Gemini 3 移行ではなく Skill にする

CLI の価値はプロンプト・スキーマ・レポート形式であり、すべて Markdown と
JSON の形をしたコンテンツである。Skill として再ホストすることで、リサーチ
フェーズは README がずっと謳ってきた姿になる: エージェントが**複数回の検索**を
実行し、**実際の ToS / プライバシーポリシー / セキュリティページを取得して
読み**、スキーマの観点が埋まるまでループし、実際に開いた URL だけを引用する。
モデル依存・GCP プロジェクト・ADC 認証・Vertex AI コスト・429 リトライ機構は
すべて消え、リポジトリは ADR-001 の移行リストから外れる。

### 2. 名前は `service-research`、対象は製品*と*サービス

`github.com/nlink-jp/product-research` は既に存在し、アーカイブ後の
リポジトリ名は再利用できない（`meeting-note` → `meeting-notes` の教訓）。
新名称は *research* のアイデンティティを保ち、SKILL.md は製品とサービスの
両方が対象であることを明示する。

### 3. JSON スキーマは構造をそのまま引き継ぐ

CLI の JSON を消費する下流ツールは今日存在しない（ワークスペース横断で
確認済み）ため、互換性はソフト制約である。スキーマはフィールド構造を
保ったまま引き継ぐ — 良い設計であり、新旧レポートの比較可能性も保たれる —
`schema.json`（Pydantic モデルから translate した JSON Schema draft）として。
stdlib のみの `scripts/validate.py` が出力レポートを検査する: スキーマ適合・
`overall_risk_level` の enum・空でない `sources`。レポートは日本語デフォルト・
要求時英語（CLI は ja 専用だった; meeting-notes と同じ拡張）。

### 4. 標準の skills-series スキャフォールド

リポジトリ = skill（ADR-004）、配布境界としての `service-research/`
サブディレクトリ、vendored な `tests/validate-skill.sh`（ADR-006）、
CONVENTIONS.md の Skill テンプレート由来の Makefile、参照形状として `rfp`
からスキャフォールド。内容: `SKILL.md`（ワークフロー; 敵対的に制御されうる
Web コンテンツを読むスキルなので、インジェクション防御を冒頭に置く）、
`schema.json`、`references/report-format.md`、`scripts/validate.py`。

## Consequences

- ADR-001 の「コード変更必須」リストが 5 リポジトリから 4 へ縮む;
  2 つの GCP プロジェクトから Vertex AI 呼び出し元が 1 つ消える。
- 旧 CLI のパイプモード（`--json-only | jq`）や Claude セッション外の
  cron/バッチ利用は失われる。既知の利用は無い; 再浮上したら Skill を
  `claude -p` でヘッドレス実行する。
- レポート品質は固定された Gemini バージョンではなくセッションモデルに
  依存して変動する — 受容。すべてのスキルに言えることと同じ。
- 出力長が単一生成の産物ではなくなるため、meeting-notes のフラグメント
  ループの動機だった切り詰め/破損クラスは、リトライで回避するのではなく
  構造的に回避される。
- カタログ面 2 つ（org profile、nlink-web-site）へのエントリ追加 1 件と、
  README ポインタ付きアーカイブ 1 件。リリースチェックリストに従う。

## Alternatives considered

| 代替案 | 不採用の理由 |
|---|---|
| GA 時に CLI を Gemini 3 へ移行 | ツールの実際の弱点である単発リサーチフェーズを温存するために、約 290 行の配管と実行ごとの Vertex コストを維持することになる |
| MCP サーバーとして再構築 | MCP が価値を持つのは状態・クレデンシャル・ローカルエンジンを仲介するとき; これは純粋なプロンプトワークフローであり、Skill という形態こそがツールである |
| CLI と Skill を並行維持 | 同じプロンプトとスキーマに 2 つの面; ドリフトが保証される（カタログ 2 面の教訓） |
| skill リポジトリに `product-research` の名前を再利用 | アーカイブ済みリポジトリが名前を保持している限り不可能; アーカイブのリネームは既存リンクを壊す |

## References

- [ADR-001](https://github.com/nlink-jp/.github/blob/main/adr/001-gemini3-migration.md) — Gemini 2.5 廃止、移行リスト
- [ADR-003](https://github.com/nlink-jp/.github/blob/main/adr/003-mcp-tactics-skill.md) — 前例: 成果物形態としての Skill
- [ADR-004](https://github.com/nlink-jp/.github/blob/main/adr/004-skills-series-umbrella.md) — リポジトリ = skill、配布境界
- [ADR-006](https://github.com/nlink-jp/.github/blob/main/adr/006-skill-validator-vendoring.md) — vendored バリデーター
- [meeting-notes](https://github.com/nlink-jp/meeting-notes) — 前例: CLI → Skill 変換
- [product-research](https://github.com/nlink-jp/product-research) — 廃止対象の CLI
