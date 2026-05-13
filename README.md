# ComfyUI-CheckpointNameCycler

おぬしはCheckpointを落としただけで満足しておらぬか？ そんなSSDの肥やしを宝の山に変える、全自動モデル巡回ノードの登場じゃ！

「色んなCheckpointを落としたけど、切り替えるのが面倒でいつも同じのを使っているのう……」

そんなおぬしのために、実行ごとにCheckpointを自動で切り替え、100件のキューも雑に捌ける巡回魔導具を用意したぞ！

## 特徴

- **実行ごとにCheckpointを自動巡回**: <br/>
切り替えモードは以下の設定を選べるぞ！
  - `increment`: 順番に。<br/>
  おぬしのライブラリを端から端まで堪能できるぞ。
  - `randomize`: 運任せ。<br/>
  予期せぬ傑作に出会えるかもしれぬな。
  - `shuffle_once`: 運任せ ＆ 一巡するまで重複なし！<br/>
  全モデルを平等に試したいおぬしへの最適解じゃ。
  - `fixed`: 固定。<br/>
  お気に入りの場所で立ち止まることも可能じゃな。 <br/>
  （`Checkpoint Name Selector`とほぼ同等機能のノードになるぞ！）

- **100件キュー投入の心強い味方**: <br/>
ブラウザの値を書き換えるのではなく、サーバー側でノードごとに状態を管理する。 <br/>
`CheckpointNameCycler` の設定が終われば、後はキューを雑に積めばいいだけのイージー設計じゃ。
- **`change_every` でじっくり比較**: <br/>
1枚ごとに変えるもよし、3枚ごとに変えて微細な差を観察するもよし。おぬしの好みに合わせて設定できるのじゃ。
- **保存名も美しく (`ckpt_name_safe`)**: <br/>
ファイル名に使えぬ文字を `_` に置換し、拡張子を削った「安全な名前」を出力する。 これでおぬしの保存フォルダもスッキリじゃな！

## 導入方法

ComfyUIの `custom_nodes` ディレクトリへ向かい、以下の呪文（コマンド）を唱えるのじゃ！

```bash
git clone https://github.com/ruminar/ComfyUI-CheckpointNameCycler.git
```

## 使い方

1. `Checkpoint Name Cycler` ノードを置く。
2. `ckpt_name` を `CheckpointLoaderSimple` などの入力へ繋ぐ。
3. `ckpt_name_safe` を `SaveImage` などの `filename_prefix` へ繋ぐ。（これが整理の鍵じゃ！）
4. `mode` と `change_every` を選び、開始位置を `start_checkpoint` で指定する。
5. あとはキューを好きなだけ積んで、お茶でも飲んで待つだけじゃ！

<br/>

<img width="856" height="478" alt="image" src="https://github.com/user-attachments/assets/f6a2c862-f255-409a-b2a6-783a7b2f569f" />

## 出力される力

- `ckpt_name`: ローダーに渡すための名前じゃ。
- `ckpt_name_str`: Checkpoint名を文字列として扱いたい時に使うのじゃ。
- `ckpt_name_safe`: ファイル名保存に便利な、整理された名前じゃ。
- `index` / `count` / `cycle`: 今どのモデルか、全部で何個あるか、何周したか……進捗確認に使えるぞ。

## 【推奨】棚卸し・整理の黄金サイクル

これと対となるノード、 **[`ComfyUI-CheckpointWidgetRefresh`](https://github.com/ruminar/ComfyUI-CheckpointWidgetRefresh)** と組み合わせることで、最強の「モデル棚卸し環境」が完成するぞ！

1. **大量出力**: <br/>
Cyclerで全モデルを回す。`ckpt_name_safe` をファイル名に使えば、どの絵がどのモデルか一目瞭然！
2. **物理整理**: <br/>
出力された絵を見て「これはちょっと好みとは違うなあ」と思ったら、SSDのモデルフォルダから直接ファイルを削除・整理するのじゃ。
3. **その場で同期**: <br/>
**`Checkpoint Widget Refresh`** をポチッ！ ComfyUIを再起動せずともリストが最新になり、Cyclerの巡回位置もリセットされるぞ。
4. **作業続行**: <br/>
淀みなく、次の「お気に入り探し」へ。

再起動の待ち時間という「魔の空白」を消し飛ばし、SSDの肥やしを鮮やかに整理してやるのじゃ！ <br/>
むろん、Checkpointがお気に入りだけになれば、あとはこの`CheckpointNameCycler`で思う存分好きな画像を出力させてお楽しみじゃ！！

## ライセンス

GPL-3.0（ComfyUI本体の掟に従っておるぞ！）

## 宣伝画像

<img width="1122" height="1402" alt="ComfyUI-CheckpointNameCycler説明画像" src="https://github.com/user-attachments/assets/3f64e207-36a3-4fec-af7d-a3cdc8427533" />
