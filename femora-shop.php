<?php
/**
 * Plugin Name: FEMORA Shop
 * Description: 下单后台专用：结账语言切换（中 / 英 / 马来）、直达结账链接、订单来源标记。此文件由代码仓库管理并自动上传，请勿在后台直接修改。
 * Version: 1.2.1
 * Author: FEMORA
 */

defined( 'ABSPATH' ) || exit;

const FM_SHOP_VERSION = '1.2.1';

/** 语言代码 => WordPress locale */
const FM_LANGS = array(
	'zh' => 'zh_CN',
	'en' => 'en_US',
	'ms' => 'ms_MY',
);

/** 购买链接里的配套代码 => WooCommerce variation ID */
const FM_PACKS = array(
	'1' => 11, // 1 盒  RM89
	'2' => 12, // 2 盒  RM159
	'4' => 13, // 3+1 盒 RM309
	'6' => 14, // 4+2 盒 RM439
);

const FM_PRODUCT_ID = 10;

/** 各语言的固定文字（产品、配套、运费、付款方式） */
const FM_TEXT = array(
	'zh' => array(
		'title'    => 'FEMORA P+ 浓缩即饮八珍',
		'packs'    => array(
			11 => '1 盒',
			12 => '2 盒',
			13 => '买 3 送 1（共 4 盒）',
			14 => '买 4 送 2（共 6 盒）',
		),
		'attr'     => '配套',
		'ship'     => array(
			'free_shipping' => '免运费',
			'flat_rate'     => '标准运费',
		),
		'pay'      => '网上付款（FPX / 电子钱包 / 信用卡）',
		'pay_desc' => '通过 Billplz 安全付款：支持 FPX 网上银行、Touch \'n Go、GrabPay 等电子钱包，以及信用卡 / 借记卡。',
	),
	'en' => array(
		'title'    => 'FEMORA P+ Bazhen with Kacip Fatimah',
		'packs'    => array(
			11 => '1 Box',
			12 => '2 Boxes',
			13 => 'Buy 3 Free 1 (4 Boxes)',
			14 => 'Buy 4 Free 2 (6 Boxes)',
		),
		'attr'     => 'Package',
		'ship'     => array(
			'free_shipping' => 'Free Shipping',
			'flat_rate'     => 'Standard Shipping',
		),
		'pay'      => 'Online Payment (FPX / E-Wallet / Card)',
		'pay_desc' => 'Pay securely via Billplz: FPX online banking, e-wallets such as Touch \'n Go and GrabPay, and credit / debit cards.',
	),
	'ms' => array(
		'title'    => 'FEMORA P+ Minuman Ekstrak Botani Bazhen dengan Kacip Fatimah',
		'packs'    => array(
			11 => '1 Kotak',
			12 => '2 Kotak',
			13 => 'Beli 3 Percuma 1 (4 Kotak)',
			14 => 'Beli 4 Percuma 2 (6 Kotak)',
		),
		'attr'     => 'Pakej',
		'ship'     => array(
			'free_shipping' => 'Penghantaran Percuma',
			'flat_rate'     => 'Penghantaran Standard',
		),
		'pay'      => 'Bayaran Dalam Talian (FPX / E-Wallet / Kad)',
		'pay_desc' => 'Bayar dengan selamat melalui Billplz: perbankan dalam talian FPX, e-wallet seperti Touch \'n Go dan GrabPay, serta kad kredit / debit.',
	),
);

/** 购物车 / 结账 / 付款成功页的页眉页脚文字 */
const FM_CHROME = array(
	'zh' => array(
		'back'    => '返回首页',
		'service' => '客服',
		'email'   => 'Email',
		'titles'  => array(
			'checkout' => '结账',
			'cart'     => '购物车',
			'received' => '订单已收到',
			'account'  => '我的账户',
		),
	),
	'en' => array(
		'back'    => 'Back to home',
		'service' => 'Customer service',
		'email'   => 'Email',
		'titles'  => array(
			'checkout' => 'Checkout',
			'cart'     => 'Cart',
			'received' => 'Order received',
			'account'  => 'My account',
		),
	),
	'ms' => array(
		'back'    => 'Kembali ke laman utama',
		'service' => 'Khidmat pelanggan',
		'email'   => 'E-mel',
		'titles'  => array(
			'checkout' => 'Pembayaran',
			'cart'     => 'Troli',
			'received' => 'Pesanan diterima',
			'account'  => 'Akaun saya',
		),
	),
);

/** 公司和客服资料（页脚用） */
const FM_COMPANY        = 'JK HEALTHY SDN. BHD. 202601003161 (1665258-D)';
const FM_WHATSAPP_TEXT  = '012-247 5798';
const FM_WHATSAPP_LINK  = 'https://wa.me/60122475798';
const FM_EMAIL          = 'admin@femoramy.com';

/** 马来文网站的网址（页眉的“返回首页”用） */
const FM_HOME_MS = 'https://femora-my.com/';

/** 订单来源代码 => 后台显示名称 */
const FM_SOURCES = array(
	'zh-site' => '中文网站',
	'en-site' => '英文网站',
	'ms-site' => '马来文网站',
);

/* -------------------------------------------------------------------------
 * 1. 语言：?lang=zh|en|ms 写入 cookie，之后的购物车 / 结账 / 付款成功页跟着走
 * ---------------------------------------------------------------------- */

function fm_setcookie( $name, $value ) {
	if ( headers_sent() ) {
		return;
	}
	setcookie(
		$name,
		$value,
		array(
			'expires'  => time() + 30 * 86400,
			'path'     => '/',
			'secure'   => ( ! empty( $_SERVER['HTTPS'] ) && 'off' !== $_SERVER['HTTPS'] ),
			'httponly' => false,
			'samesite' => 'Lax',
		)
	);
	$_COOKIE[ $name ] = $value;
}

/** 顾客选的语言（zh / en / ms），没有选过则为 null */
function fm_lang() {
	static $lang = false;
	if ( false !== $lang ) {
		return $lang;
	}
	$lang = null;
	if ( isset( $_GET['lang'] ) && is_string( $_GET['lang'] ) && isset( FM_LANGS[ $_GET['lang'] ] ) ) {
		$lang = $_GET['lang'];
		fm_setcookie( 'fm_lang', $lang );
	} elseif ( isset( $_COOKIE['fm_lang'] ) && is_string( $_COOKIE['fm_lang'] ) && isset( FM_LANGS[ $_COOKIE['fm_lang'] ] ) ) {
		$lang = $_COOKIE['fm_lang'];
	}
	return $lang;
}

/** 只在购物车 / 结账 / 账户页和它们的接口请求生效，不影响后台和其他（有缓存的）页面 */
function fm_is_shop_request() {
	static $is = null;
	if ( null !== $is ) {
		return $is;
	}
	$uri  = isset( $_SERVER['REQUEST_URI'] ) ? rawurldecode( (string) $_SERVER['REQUEST_URI'] ) : '';
	$path = (string) parse_url( $uri, PHP_URL_PATH );
	if ( 0 === strpos( $path, '/wp-admin' ) || 0 === strpos( $path, '/wp-login' ) ) {
		$is = false;
	} elseif ( preg_match( '#^/(?:zh/)?(?:cart|checkout|my-account)(?:/|$)#', $path ) ) {
		$is = true;
	} elseif ( false !== strpos( $uri, '/wc/store' ) || isset( $_GET['wc-ajax'] ) ) {
		$is = true;
	} else {
		$is = false;
	}
	return $is;
}

/** 当前请求要用的语言；不属于下单流程或顾客没选语言时为 null */
function fm_active_lang() {
	return fm_is_shop_request() ? fm_lang() : null;
}

// 尽早读取参数并写 cookie（此时还没有任何输出）。
if ( ! defined( 'WP_CLI' ) ) {
	fm_lang();
	if ( isset( $_GET['src'] ) && is_string( $_GET['src'] ) && preg_match( '/^[a-z0-9_-]{1,32}$/', $_GET['src'] ) ) {
		fm_setcookie( 'fm_src', $_GET['src'] );
	}
}

function fm_filter_locale( $locale ) {
	$lang = fm_active_lang();
	return $lang ? FM_LANGS[ $lang ] : $locale;
}
// 优先级放到最后，盖过 TranslatePress 对默认语言的设定。
add_filter( 'locale', 'fm_filter_locale', PHP_INT_MAX );
add_filter( 'determine_locale', 'fm_filter_locale', PHP_INT_MAX );
add_filter( 'pre_determine_locale', function ( $locale ) {
	$lang = fm_active_lang();
	return $lang ? FM_LANGS[ $lang ] : $locale;
}, PHP_INT_MAX );

/* -------------------------------------------------------------------------
 * 2. 产品、配套、运费、付款方式的名称按语言显示
 * ---------------------------------------------------------------------- */

function fm_text( $key, $lang = null ) {
	$lang = $lang ? $lang : fm_active_lang();
	return ( $lang && isset( FM_TEXT[ $lang ][ $key ] ) ) ? FM_TEXT[ $lang ][ $key ] : null;
}

/** 产品或配套的显示名称；$full 为 true 时配套名称前面带产品名 */
function fm_product_name( $id, $lang, $full = true ) {
	$id = (int) $id;
	if ( ! $lang || ! isset( FM_TEXT[ $lang ] ) ) {
		return null;
	}
	$t = FM_TEXT[ $lang ];
	if ( FM_PRODUCT_ID === $id ) {
		return $t['title'];
	}
	if ( isset( $t['packs'][ $id ] ) ) {
		return $full ? $t['title'] . ' – ' . $t['packs'][ $id ] : $t['packs'][ $id ];
	}
	return null;
}

add_filter(
	'woocommerce_product_title',
	function ( $title, $product = null ) {
		$lang = fm_active_lang();
		if ( $lang && $product instanceof WC_Product ) {
			$pid = $product->is_type( 'variation' ) ? $product->get_parent_id() : $product->get_id();
			if ( FM_PRODUCT_ID === (int) $pid ) {
				return FM_TEXT[ $lang ]['title'];
			}
		}
		return $title;
	},
	20,
	2
);

function fm_filter_product_name( $name, $product = null ) {
	$lang = fm_active_lang();
	if ( $lang && $product instanceof WC_Product ) {
		$translated = fm_product_name( $product->get_id(), $lang, true );
		if ( $translated ) {
			return $translated;
		}
	}
	return $name;
}
add_filter( 'woocommerce_product_get_name', 'fm_filter_product_name', 20, 2 );
add_filter( 'woocommerce_product_variation_get_name', 'fm_filter_product_name', 20, 2 );

/** 配套属性的名称（“配套 Package”） */
add_filter(
	'woocommerce_attribute_label',
	function ( $label ) {
		$t = fm_text( 'attr' );
		return ( $t && false !== strpos( (string) $label, 'Package' ) ) ? $t : $label;
	},
	20
);

/** 把后台存的配套选项（如“2盒 · 2 Boxes”）换成当前语言 */
function fm_pack_option( $value, $lang ) {
	static $map = null;
	if ( null === $map ) {
		$map = array(
			'1盒 · 1 Box'      => 11,
			'2盒 · 2 Boxes'    => 12,
			'3+1盒 · 4 Boxes'  => 13,
			'4+2盒 · 6 Boxes'  => 14,
		);
	}
	$value = (string) $value;
	if ( $lang && isset( $map[ $value ] ) ) {
		return FM_TEXT[ $lang ]['packs'][ $map[ $value ] ];
	}
	return $value;
}

add_filter(
	'woocommerce_variation_option_name',
	function ( $value ) {
		return fm_pack_option( $value, fm_active_lang() );
	},
	20
);

/** 运费名称；并把语言放进运费缓存的识别码，换语言时会重新计算 */
add_filter(
	'woocommerce_cart_shipping_packages',
	function ( $packages ) {
		$lang = fm_active_lang();
		if ( $lang && is_array( $packages ) ) {
			foreach ( $packages as $i => $package ) {
				$packages[ $i ]['fm_lang'] = $lang;
			}
		}
		return $packages;
	},
	20
);

add_filter(
	'woocommerce_package_rates',
	function ( $rates ) {
		$labels = fm_text( 'ship' );
		if ( $labels && is_array( $rates ) ) {
			foreach ( $rates as $rate ) {
				if ( is_object( $rate ) && method_exists( $rate, 'get_method_id' ) && isset( $labels[ $rate->get_method_id() ] ) ) {
					$rate->set_label( $labels[ $rate->get_method_id() ] );
				}
			}
		}
		return $rates;
	},
	200
);

/** Billplz 付款方式的标题和说明 */
add_filter(
	'option_woocommerce_billplz_settings',
	function ( $settings ) {
		$lang = fm_active_lang();
		if ( $lang && is_array( $settings ) ) {
			$settings['title']       = FM_TEXT[ $lang ]['pay'];
			$settings['description'] = FM_TEXT[ $lang ]['pay_desc'];
		}
		return $settings;
	},
	20
);

/* -------------------------------------------------------------------------
 * 2b. 马来文界面文字
 *     WooCommerce 官方没有马来文语言包，结账流程的文字由 lang/ms.php 提供。
 * ---------------------------------------------------------------------- */

function fm_ms_map() {
	static $map = null;
	if ( null === $map ) {
		$file = __DIR__ . '/lang/ms.php';
		$map  = is_readable( $file ) ? (array) include $file : array();
	}
	return $map;
}

function fm_ms_lookup( $translation, $text, $domain ) {
	if ( 'woocommerce' !== $domain ) {
		return $translation;
	}
	$map = fm_ms_map();
	return isset( $map[ $text ] ) ? $map[ $text ] : $translation;
}

if ( 'ms' === fm_active_lang() ) {
	add_filter( 'gettext', 'fm_ms_lookup', 20, 3 );
	add_filter(
		'gettext_with_context',
		function ( $translation, $text, $context, $domain ) {
			return fm_ms_lookup( $translation, $text, $domain );
		},
		20,
		4
	);
	add_filter(
		'ngettext',
		function ( $translation, $single, $plural, $number, $domain ) {
			return fm_ms_lookup( $translation, $single, $domain );
		},
		20,
		5
	);
	add_filter(
		'ngettext_with_context',
		function ( $translation, $single, $plural, $number, $context, $domain ) {
			return fm_ms_lookup( $translation, $single, $domain );
		},
		20,
		6
	);

	// 结账页是用 JavaScript 画出来的，同一份文字也要交给前端。
	add_action(
		'wp_enqueue_scripts',
		function () {
			$data = array(
				'' => array(
					'domain'       => 'messages',
					'lang'         => 'ms',
					'plural-forms' => 'nplurals=1; plural=0;',
				),
			);
			foreach ( fm_ms_map() as $source => $target ) {
				$data[ $source ] = array( $target );
			}
			wp_add_inline_script( 'wp-i18n', 'wp.i18n.setLocaleData(' . wp_json_encode( $data ) . ',"woocommerce");', 'after' );
		},
		1
	);
}

/** 页面的 lang 属性跟着顾客的语言 */
add_filter(
	'language_attributes',
	function ( $output ) {
		$lang = fm_active_lang();
		if ( $lang ) {
			$code   = str_replace( '_', '-', FM_LANGS[ $lang ] );
			$output = preg_replace( '/lang="[^"]*"/', 'lang="' . esc_attr( $code ) . '"', (string) $output );
		}
		return $output;
	},
	PHP_INT_MAX
);

/* -------------------------------------------------------------------------
 * 2c. 下单流程的页眉、页脚和页面标题按语言显示
 *     （原本的页眉页脚是中文网站的导航，马来文 / 英文顾客看不懂）
 * ---------------------------------------------------------------------- */

function fm_home_url( $lang ) {
	if ( 'ms' === $lang ) {
		return FM_HOME_MS;
	}
	return 'en' === $lang ? home_url( '/en/' ) : home_url( '/' );
}

add_filter(
	'render_block',
	function ( $content, $block ) {
		if ( empty( $block['blockName'] ) || 'core/template-part' !== $block['blockName'] ) {
			return $content;
		}
		$lang = fm_active_lang();
		if ( ! $lang ) {
			return $content;
		}
		$slug = isset( $block['attrs']['slug'] ) ? (string) $block['attrs']['slug'] : '';
		$t    = FM_CHROME[ $lang ];
		$home = esc_url( fm_home_url( $lang ) );

		if ( 'header' === $slug || 'checkout-header' === $slug ) {
			return '<header class="fm-shop-header"><a class="fm-shop-logo" href="' . $home . '">FEMORA</a>' .
				'<a class="fm-shop-back" href="' . $home . '">&larr; ' . esc_html( $t['back'] ) . '</a></header>';
		}
		if ( 'footer' === $slug ) {
			return '<footer class="fm-shop-footer">' .
				'<p>' . esc_html( $t['service'] ) . ' &mdash; WhatsApp: <a href="' . esc_url( FM_WHATSAPP_LINK ) . '">' . esc_html( FM_WHATSAPP_TEXT ) . '</a>' .
				' &middot; ' . esc_html( $t['email'] ) . ': <a href="mailto:' . esc_attr( FM_EMAIL ) . '">' . esc_html( FM_EMAIL ) . '</a></p>' .
				'<p>' . esc_html( FM_COMPANY ) . '</p>' .
				'<p>&copy; ' . esc_html( gmdate( 'Y' ) ) . ' FEMORA</p></footer>';
		}
		return $content;
	},
	20,
	2
);

add_action(
	'wp_head',
	function () {
		if ( ! fm_active_lang() ) {
			return;
		}
		echo '<style id="fm-shop-chrome">' .
			'.fm-shop-header{display:flex;align-items:center;justify-content:space-between;gap:16px;width:calc(100% - 48px);max-width:1230px;margin:0 auto;padding:18px 0}' .
			'.fm-shop-logo{font-family:"Noto Serif SC","Songti SC",STSong,"Source Han Serif SC",serif;font-size:22px;font-weight:700;letter-spacing:.18em;color:#8E1B2E;text-decoration:none}' .
			'.fm-shop-back{font-size:14px;color:#3A2A2C;text-decoration:none;white-space:nowrap}' .
			'.fm-shop-back:hover{color:#8E1B2E}' .
			'.fm-shop-footer{background:#2E0B12;color:#E8CDD2;text-align:center;padding:28px 24px;font-size:13px;line-height:1.9;margin-top:56px}' .
			'.fm-shop-footer p{margin:0}' .
			'.fm-shop-footer a{color:#fff;text-decoration:none}' .
			'.trp-language-switcher.trp-floating-switcher{display:none!important}' .
			'</style>';
	},
	50
);

add_filter(
	'document_title_parts',
	function ( $parts ) {
		$lang = fm_active_lang();
		if ( ! $lang || ! function_exists( 'is_checkout' ) ) {
			return $parts;
		}
		$titles = FM_CHROME[ $lang ]['titles'];
		if ( function_exists( 'is_order_received_page' ) && is_order_received_page() ) {
			$parts['title'] = $titles['received'];
		} elseif ( is_checkout() ) {
			$parts['title'] = $titles['checkout'];
		} elseif ( is_cart() ) {
			$parts['title'] = $titles['cart'];
		} elseif ( is_account_page() ) {
			$parts['title'] = $titles['account'];
		}
		return $parts;
	},
	PHP_INT_MAX
);

/* -------------------------------------------------------------------------
 * 3. 直达结账链接：/checkout/?fm_buy=2&lang=ms&src=ms-site
 *    清空购物车，放入所选配套 1 份，然后转到结账页（保留广告追踪参数）
 * ---------------------------------------------------------------------- */

add_action(
	'wp_loaded',
	function () {
		if ( empty( $_GET['fm_buy'] ) || ! is_string( $_GET['fm_buy'] ) ) {
			return;
		}
		if ( ! function_exists( 'WC' ) || ! WC()->cart ) {
			return;
		}
		nocache_headers();
		header( 'X-LiteSpeed-Cache-Control: no-cache' );

		$key = $_GET['fm_buy'];
		$url = wc_get_checkout_url();

		if ( isset( FM_PACKS[ $key ] ) ) {
			$variation = wc_get_product( FM_PACKS[ $key ] );
			if ( $variation && $variation->is_type( 'variation' ) && $variation->is_purchasable() && $variation->is_in_stock() ) {
				WC()->cart->empty_cart();
				WC()->cart->add_to_cart( $variation->get_parent_id(), 1, $variation->get_id(), $variation->get_variation_attributes() );
			}
		}

		$keep = array();
		foreach ( $_GET as $name => $value ) {
			if ( is_string( $value ) && ( 0 === strpos( (string) $name, 'utm_' ) || in_array( $name, array( 'fbclid', 'gclid', 'ttclid' ), true ) ) ) {
				$keep[ $name ] = rawurlencode( sanitize_text_field( wp_unslash( $value ) ) );
			}
		}
		if ( $keep ) {
			$url = add_query_arg( $keep, $url );
		}
		wp_safe_redirect( $url );
		exit;
	},
	15
);

/* -------------------------------------------------------------------------
 * 4. 订单：记录语言和来源；订单里的产品名称统一用后台原名，方便出货
 * ---------------------------------------------------------------------- */

function fm_tag_order( $order ) {
	if ( ! $order instanceof WC_Order ) {
		return;
	}
	$changed = false;
	$lang    = fm_lang();
	if ( $lang && ! $order->get_meta( '_fm_lang' ) ) {
		$order->update_meta_data( '_fm_lang', $lang );
		$changed = true;
	}
	if ( ! $order->get_meta( '_fm_source' ) && ! empty( $_COOKIE['fm_src'] ) && is_string( $_COOKIE['fm_src'] ) && preg_match( '/^[a-z0-9_-]{1,32}$/', $_COOKIE['fm_src'] ) ) {
		$order->update_meta_data( '_fm_source', $_COOKIE['fm_src'] );
		$changed = true;
	}
	if ( $changed && $order->get_id() ) {
		$order->save_meta_data();
	}
}
add_action( 'woocommerce_checkout_create_order', 'fm_tag_order', 10, 1 );
add_action( 'woocommerce_store_api_checkout_update_order_meta', 'fm_tag_order', 10, 1 );

add_action(
	'woocommerce_checkout_create_order_line_item',
	function ( $item, $cart_item_key, $values ) {
		if ( isset( $values['data'] ) && $values['data'] instanceof WC_Product ) {
			// WooCommerce 会在配套名称中间放 <span> - </span>，去掉标签，导出表格才干净。
			$item->set_name( wp_strip_all_tags( $values['data']->get_name( 'edit' ) ) );
		}
	},
	20,
	3
);

/** 顾客看到的订单页（付款成功页、我的订单）按语言显示名称 */
add_filter(
	'woocommerce_order_item_name',
	function ( $html, $item = null ) {
		$lang = fm_active_lang();
		if ( $lang && $item instanceof WC_Order_Item_Product ) {
			$id   = $item->get_variation_id() ? $item->get_variation_id() : $item->get_product_id();
			$name = fm_product_name( $id, $lang, true );
			if ( $name ) {
				return esc_html( $name );
			}
		}
		return $html;
	},
	20,
	2
);

add_filter(
	'woocommerce_order_item_display_meta_key',
	function ( $key ) {
		$t = fm_text( 'attr' );
		return ( $t && false !== strpos( (string) $key, 'Package' ) ) ? $t : $key;
	},
	20
);

add_filter(
	'woocommerce_order_item_display_meta_value',
	function ( $value ) {
		$lang = fm_active_lang();
		return $lang ? fm_pack_option( wp_strip_all_tags( (string) $value ), $lang ) : $value;
	},
	20
);

/* -------------------------------------------------------------------------
 * 5. 后台订单列表：加一栏“来源 / 语言”
 * ---------------------------------------------------------------------- */

function fm_order_origin_label( $order ) {
	if ( ! $order instanceof WC_Order ) {
		return '';
	}
	if ( 'admin' === $order->get_created_via() ) {
		return '后台录入';
	}
	$names = array(
		'zh' => '中文',
		'en' => 'English',
		'ms' => 'Melayu',
	);
	$parts = array();
	$src   = (string) $order->get_meta( '_fm_source' );
	$lang  = (string) $order->get_meta( '_fm_lang' );
	if ( '' !== $src ) {
		$parts[] = isset( FM_SOURCES[ $src ] ) ? FM_SOURCES[ $src ] : $src;
	}
	if ( isset( $names[ $lang ] ) ) {
		$parts[] = $names[ $lang ];
	}
	return $parts ? implode( ' · ', $parts ) : '—';
}

function fm_order_columns( $columns ) {
	$out = array();
	foreach ( (array) $columns as $key => $label ) {
		$out[ $key ] = $label;
		if ( 'order_status' === $key ) {
			$out['fm_origin'] = '来源 / 语言';
		}
	}
	if ( ! isset( $out['fm_origin'] ) ) {
		$out['fm_origin'] = '来源 / 语言';
	}
	return $out;
}
add_filter( 'woocommerce_shop_order_list_table_columns', 'fm_order_columns', 20 );
add_filter( 'manage_edit-shop_order_columns', 'fm_order_columns', 20 );

add_action(
	'woocommerce_shop_order_list_table_custom_column',
	function ( $column, $order ) {
		if ( 'fm_origin' === $column ) {
			echo esc_html( fm_order_origin_label( $order ) );
		}
	},
	10,
	2
);

add_action(
	'manage_shop_order_posts_custom_column',
	function ( $column, $post_id ) {
		if ( 'fm_origin' === $column && function_exists( 'wc_get_order' ) ) {
			echo esc_html( fm_order_origin_label( wc_get_order( $post_id ) ) );
		}
	},
	10,
	2
);

/* -------------------------------------------------------------------------
 * 6. 维护接口
 *    GET  /wp-json/fm/v1/version       公开，只回版本号，用来确认上传成功
 *    POST /wp-json/fm/v1/install-lang  仅管理员，安装马来文语言包
 * ---------------------------------------------------------------------- */

add_action(
	'rest_api_init',
	function () {
		register_rest_route(
			'fm/v1',
			'/version',
			array(
				'methods'             => 'GET',
				'permission_callback' => '__return_true',
				'callback'            => function () {
					return array( 'version' => FM_SHOP_VERSION );
				},
			)
		);

		register_rest_route(
			'fm/v1',
			'/install-lang',
			array(
				'methods'             => 'POST',
				'permission_callback' => function () {
					return current_user_can( 'manage_options' );
				},
				'callback'            => function () {
					require_once ABSPATH . 'wp-admin/includes/file.php';
					require_once ABSPATH . 'wp-admin/includes/misc.php';
					require_once ABSPATH . 'wp-admin/includes/translation-install.php';
					require_once ABSPATH . 'wp-admin/includes/class-wp-upgrader.php';

					$out = array();
					foreach ( FM_LANGS as $locale ) {
						if ( 'en_US' === $locale ) {
							continue;
						}
						$out[ 'core_' . $locale ] = wp_download_language_pack( $locale );
					}

					wp_clean_update_cache();
					wp_update_plugins();
					wp_update_themes();

					$upgrader      = new Language_Pack_Upgrader( new Automatic_Upgrader_Skin() );
					$result        = $upgrader->bulk_upgrade();
					$out['packs']  = is_array( $result ) ? count( $result ) : $result;
					$out['langs']  = get_available_languages();
					$out['wc_ms']  = file_exists( WP_LANG_DIR . '/plugins/woocommerce-ms_MY.mo' ) || file_exists( WP_LANG_DIR . '/plugins/woocommerce-ms_MY.l10n.php' );
					$out['wc_ms_js'] = count( (array) glob( WP_LANG_DIR . '/plugins/woocommerce-ms_MY-*.json' ) );
					return $out;
				},
			)
		);
	}
);

/* -------------------------------------------------------------------------
 * 7. 翻译工具：网址加 ?fm_i18n_log=1 时，记录页面实际用到的界面文字
 *    （只列出文字本身，用来核对马来文翻译有没有漏）
 * ---------------------------------------------------------------------- */

if ( isset( $_GET['fm_i18n_log'] ) ) {
	$GLOBALS['fm_i18n_seen'] = array();

	$fm_i18n_collect = function ( $key, $domain ) {
		if ( ! is_admin() ) {
			$GLOBALS['fm_i18n_seen'][ $domain . '|' . $key ] = 1;
		}
	};

	add_filter(
		'gettext',
		function ( $translation, $text, $domain ) use ( $fm_i18n_collect ) {
			$fm_i18n_collect( $text, $domain );
			return $translation;
		},
		5,
		3
	);
	add_filter(
		'gettext_with_context',
		function ( $translation, $text, $context, $domain ) use ( $fm_i18n_collect ) {
			$fm_i18n_collect( $context . "\x04" . $text, $domain );
			return $translation;
		},
		5,
		4
	);
	add_filter(
		'ngettext',
		function ( $translation, $single, $plural, $number, $domain ) use ( $fm_i18n_collect ) {
			$fm_i18n_collect( $single, $domain );
			return $translation;
		},
		5,
		5
	);

	add_action(
		'wp_enqueue_scripts',
		function () {
			$js = "(function(){var S=window.__fmI18n={};function a(k,d){S[(d||'default')+'|'+k]=1;}" .
				"wp.hooks.addFilter('i18n.gettext','fm/log',function(t,x,d){a(x,d);return t;});" .
				"wp.hooks.addFilter('i18n.gettext_with_context','fm/log',function(t,x,c,d){a(c+'\\u0004'+x,d);return t;});" .
				"wp.hooks.addFilter('i18n.ngettext','fm/log',function(t,s,p,n,d){a(s,d);return t;});" .
				"wp.hooks.addFilter('i18n.ngettext_with_context','fm/log',function(t,s,p,n,c,d){a(c+'\\u0004'+s,d);return t;});})();";
			wp_add_inline_script( 'wp-i18n', $js, 'after' );
		},
		1
	);

	add_action(
		'wp_footer',
		function () {
			$keys = array();
			foreach ( array_keys( $GLOBALS['fm_i18n_seen'] ) as $key ) {
				if ( 0 !== strpos( $key, 'default|' ) ) {
					$keys[] = $key;
				}
			}
			echo '<script>window.__fmPhpI18n=' . wp_json_encode( $keys ) . ';</script>';
		},
		9999
	);
}
