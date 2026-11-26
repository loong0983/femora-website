# FEMORA Shop（下单后台插件）

这个分支只放 WooCommerce 下单后台用的插件，Hostinger 会把它拉到
`wp-content/plugins/femora-shop/`。

- `femora-shop.php`：结账语言切换（中 / 英 / 马来）、直达结账链接、订单来源标记。

## 怎么更新

1. 改 `femora-shop.php`，并把文件顶部的 `Version` 和 `FM_SHOP_VERSION` 加一
2. `php -l femora-shop.php` 检查语法（语法错误会让整个网站打不开）
3. 推到 `shop` 分支
4. 在 Hostinger 触发一次 Git 拉取（`hosting_git_deploy-website-repository`，
   directory = `wp-content/plugins/femora-shop`，branch = `shop`）
5. 打开 `/wp-json/fm/v1/version` 确认版本号已更新

## 购买链接格式

`/checkout/?fm_buy=<配套>&lang=<语言>&src=<来源>`

- 配套：`1`（1 盒）、`2`（2 盒）、`4`（3+1 盒）、`6`（4+2 盒）
- 语言：`zh`、`en`、`ms`
- 来源：`zh-site`、`en-site`、`ms-site`
