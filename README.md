# ACTGS2ONS_Actress_Nijimite
## なにこれ
  2004年にACTRESS様から発売された、18禁PC向けノベルゲーム'[虹を見つけたら教えて。](https://www.actress.ne.jp/products/nijimite/index.html)'を<br>
  ONScripter形式へ変換するためのコンバータです<br>

## 再現度
原作との違いは主に以下
 - select2命令の処理が不安定(ってか完成してない)
 - 選択肢でウィンドウが切り替わらない
 - セーブ/ロード画面は超簡略化
 - CG/回想モードは未実装

v0.9.0現在では未完成品です<br>
特定のルートに行けない可能性があります<br>
(どうも音海TRUE ENDへのフラグ管理が怪しい)<br>


## 使い方
 1. 適当な作業フォルダを作成
 2. [GARBro](https://drive.google.com/file/d/1gH9nNRxaz8GexN0B1hWyUc3o692bkWXX/view)で以下のアーカイブを作業フォルダへ展開<br>
    
     - Arc.wav →wav
     - Arc.scr →scr
     - Arc.cg →cg

     設定は以下の通り↓<br>
     ![](image1-1.png)<br>
     ![](image1-2.png)<br>
 3. ゲーム側の設定用の.iniファイル、及び動画(.mpgとセーブ以外の.dat全て)を作業フォルダへコピー
 4. 展開先のディレクトリで[このコンバータ](https://github.com/Prince-of-sea/ACTGS2ONS_Actress_Nijimite/releases/latest)をDL/起動させ変換(最低でも数分程度はかかります)<br>
    変換前の時点で以下のような構成になっていればOKです↓<br>
    ![](image2.png)<br>
 5. ウィンドウが消え、0.txtができれば完成<br>
    変換前の"wav"フォルダ、ini等の不要データを削除し、変換済みファイルと共に利用ハードへ転送


## 注意事項
 - 当然ですが公式ツールではありません
 - __FANZA DL版で動作確認しています__ パッケージ版の動作は未確認
 - 本ツールの使用において生じた問題や不利益などについて、作者は一切の責任を負いません

## その他
 - 本作の変換を追加でサポートする[PSP向け自動変換ツール作ってます](https://github.com/Prince-of-sea/ONScripter_Multi_Converter)<br>
    もしPSPで遊ぶ場合はぜひご利用ください(v1.2.8以上推奨)
 - 一応、他のACTGS作品にも流用できるように制作しています(800x600限定)<br>
    動作の安定性は全く保証できませんが、試してみてもいいかも...?