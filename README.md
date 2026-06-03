# 複雑理工学実験概論 生体計測グループ

- [第1回 オンライン: スマートウォッチ等に実装されている光による脈拍計測の原理とオンラインシミュレータでのプロトタイピング](https://shinolab.github.io/cmplx-exp-class/session1.html)
- [第2回 対面: 現実世界のノイズとエンジニアリングによる解決](https://shinolab.github.io/cmplx-exp-class/session2.html)

スライドは[Marp](https://marp.app/)で書いてある.
グラフや回路図はPythonで生成.

---

## 1. クイックスタート

[`marp-cli`](https://github.com/marp-team/marp-cli) と [`uv`](https://docs.astral.sh/uv/) をインストールして, 以下のコマンドを実行.

```bash
git clone https://github.com/shinolab/cmplx-exp-class.git
make setup
make all
```

## 2. ディレクトリ構成

```
.
├── README.md
├── Makefile
├── slides/
│   ├── session1.md      : 第1回のスライド
│   ├── session2.md      : 第2回のスライド
│   ├── theme/
│   │   └── main.css
│   └── figures/         : 図. 直接編集せず, gen_figures.py で生成する
│       └── drawio/      : 手書きの図
├── scripts/
│   └── gen_figures.py   : 図を生成するスクリプト
└── out/                 : スライド生成結果
```

---

## 3. ビルドコマンド一覧

| コマンド | 動作 |
|---|---|
| `make setup` | 依存を導入 (初回のみ) |
| `make` / `make all` | 図を生成し, 両回のスライドを `out/` に出力 |
| `make figures` | 図だけ再生成 |
| `make pdf` | PDFだけ再生成 |
| `make watch` | プレビュー |
| `make clean` | 生成物を削除 |
