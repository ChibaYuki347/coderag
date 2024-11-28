# 概要

コード理解やコード作成をするためのベースツールです。

azure developer cliを使ってリソースの作成や削除を行うことができます。

# 事前準備
- [azure developer cli](https://learn.microsoft.com/ja-jp/azure/developer/azure-developer-cli/overview?tabs=windows)のインストール
 - azd auth loginコマンドを実行してAzureにログインする
  ```
  azd auth login
  ```
- Contributer、及びのアクセス権を持ったAzureサブスクリプションの作成
- [Python](https://www.python.org/downloads/)のインストール(3.10以上を推奨)
- Windowsの場合
  - [PowerShell Coreのインストール](https://learn.microsoft.com/ja-jp/powershell/scripting/install/installing-powershell-on-windows?view=powershell-7.4)
  - PowerShellの実行ポリシーを変更する
    ```
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    ```
- Linux, macの場合
  - scriptsフォルダ内のスクリプトを実行するために権限を付与する
    ```
    chmod +x scripts/*.sh
    ```

# 使い方
dataフォルダにコードやドキュメントを格納します。
コードは/data/codeに格納し、ドキュメントは/data/docsに格納します。

複数階層になっていても、再帰的にファイルを取得します。

下記は例です。

```
- data
  - code
    - Script
     - common.js
    - Styles
        - base.css
    - samplecript.xx
  - docs
    - コーディング規約.md
    - 開発部.NETコーディング規約.pdf
```
ドキュメントに関してはmarkdown、およびpdfファイルのみ対応しています。そのためExcelやWordファイルはあらかじめpdfに変換してください。

# インフラの構築

```bash
azd provision
```

# インフラの削除

```bash
azd down
```

# スクリプト一覧

## データソースの取得:コードとドキュメントを取得しデータベース(SQLite)に格納する

Windows 

```bash
.\script\codeindex.ps1
```

Linux, Mac

```bash
./script/codeindex.sh
```






    