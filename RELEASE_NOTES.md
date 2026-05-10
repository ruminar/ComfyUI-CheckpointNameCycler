# v0.1.0

初回リリースじゃ！

## 特徴

- 実行ごとにCheckpointを自動で切り替え
- `fixed` / `increment` / `randomize` / `shuffle_once` に対応
- `change_every` で、同じCheckpointを何枚ずつ使うか指定可能
- `start_checkpoint` で開始位置を指定可能
- `ckpt_name_safe` により、保存ファイル名向けの安全なCheckpoint名を出力
- 100件キュー投入のような大量比較・棚卸し用途を想定

## 使い方

1. `Checkpoint Name Cycler` ノードを置く
2. `ckpt_name` を `CheckpointLoaderSimple` などへ接続
3. `ckpt_name_safe` を `SaveImage` の `filename_prefix` などへ接続
4. `mode` と `change_every` を設定
5. キューを投入してCheckpointを比較

## 推奨連携

`ComfyUI-CheckpointWidgetRefresh` と組み合わせることで、Checkpoint追加・削除後もComfyUIを再起動せずに選択リストを更新できます。
