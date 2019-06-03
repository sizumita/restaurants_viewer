# restaurants_viewer
View restaurants possession in ARKit on Pythonista!

# How to use
- このリポジトリをクローンします。
- token.txtを作成し、 [こちら](http://webservice.recruit.co.jp/hotpepper/reference.html) のグルメーサーチAPIのトークンを書き込みます。
- Pythonistaで、`true_heading.py`を実行して、表示されるまで待ちましょう。
- 終了するときはPythonistaを履歴から削除して停止させてください。

# Important point
- 起動した際に、位置情報のズレや、作者にもわからない謎のズレが発生することがあります。その場合は再起動してください。

# List of Functions
- ARKitで、APIから取得したレストランの位置に柱を立てる
- 100m以内にある柱はdeepskyblue、それ以上はblueで表示される
- 柱がくるくる回っている
- 柱の横に店名と最初の位置からの長さが書かれた文字が浮かぶ
- 文字はくるくる回りながら上下に移動する
