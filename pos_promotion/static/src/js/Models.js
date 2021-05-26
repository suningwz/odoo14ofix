"use strict";
odoo.define('Models', function (require) {

    var models = require('point_of_sale.models');

    models.load_models([
        {
            model: 'coupon.program',
            fields: [
                'name',
                'rule_id',
                'reward_id',
                'sequence',
                'maximum_use_number',
                'program_type',
                'promo_code_usage',
                'promo_code',
                'promo_applicability',
                'coupon_ids',
                'coupon_count',
                'validity_duration',
            ],
            domain: function (self) {
                return [['company_id', '=', self.company.id]]
            },
            loaded: function (self, couponPrograms) {
                self.couponProgramsAutomatic = [];
                self.couponRule_ids = [];
                self.couponReward_ids = [];
                self.couponProgram_by_code = {};
                self.couponProgram_by_id = {};
                self.couponProgram_ids = [];
                self.couponPrograms = couponPrograms;
                self.couponPrograms.forEach(p => {
                    if (!self.couponRule_ids.includes(p.rule_id[0])) {
                        self.couponRule_ids.push(p.rule_id[0])
                    }
                    if (!self.couponReward_ids.includes(p.rule_id[0])) {
                        self.couponReward_ids.push(p.reward_id[0])
                    }
                    if (p.promo_code) {
                        self.couponProgram_by_code[p.promo_code] = p
                    }
                    self.couponProgram_by_id[p.id] = p;
                    self.couponProgram_ids.push(p.id)
                    if (self.config.coupon_program_ids.includes(p.id)) {
                        self.couponProgramsAutomatic.push(p)
                    }
                })

            }
        },
        {
            model: 'coupon.coupon',
            fields: [
                'code',
                'expiration_date',
                'state',
                'partner_id',
                'program_id',
                'discount_line_product_id',
            ],
            domain: function (self) {
                return [['state', 'in', ['new', 'sent']], ['program_id', 'in', self.couponProgram_ids]]
            },
            loaded: function (self, coupons) {
                self.coupons = coupons;
                self.coupon_by_code = {};
                self.coupon_by_id = {};
                self.coupon_ids = [];
                self.coupons.forEach(c => {
                    self.coupon_by_id[c.id] = c;
                    self.coupon_ids.push(c.id)
                    self.coupon_by_code[c.code] = c
                })
            }
        },
        {
            model: 'coupon.rule',
            fields: [
                'rule_date_from',
                'rule_date_to',
                'rule_partners_domain',
                'rule_products_domain',
                'rule_min_quantity',
                'rule_minimum_amount',
                'rule_minimum_amount_tax_inclusion',
                'applied_partner_ids',
                'applied_product_ids',
            ],
            domain: function (self) {
                return [['id', 'in', self.couponRule_ids]]
            },
            loaded: function (self, couponRules) {
                self.couponRules = couponRules;
                self.couponRule_by_id = {};
                self.couponRule_ids = [];
                self.couponRules.forEach(r => {
                    self.couponRule_by_id[r.id] = r;
                    self.couponRule_ids.push(r.id)
                })
            }
        },
        {
            model: 'coupon.reward',
            fields: [
                'reward_type',
                'reward_product_id',
                'reward_product_quantity',
                'discount_type',
                'discount_percentage',
                'discount_apply_on',
                'discount_specific_product_ids',
                'discount_max_amount',
                'discount_fixed_amount',
                'discount_line_product_id',
            ],
            domain: function (self) {
                return [['id', 'in', self.couponReward_ids]]
            },
            loaded: function (self, couponRewards) {
                self.reward_product_ids = []
                self.couponRewards = couponRewards;
                self.couponReward_by_id = {};
                self.couponReward_ids = [];
                self.couponRewards.forEach(rw => {
                    self.couponReward_by_id[rw.id] = rw;
                    self.couponReward_ids.push(rw.id)
                    if (rw.reward_product_id) {
                        self.reward_product_ids.push(rw.reward_product_id[0])
                    }
                    if (rw.discount_line_product_id) {
                        self.reward_product_ids.push(rw.discount_line_product_id[0])
                    }
                })
            }
        },
        {
            model: 'product.product',
            fields: ['display_name', 'lst_price', 'standard_price', 'categ_id', 'pos_categ_id', 'taxes_id',
                'barcode', 'default_code', 'to_weight', 'uom_id', 'description_sale', 'description',
                'product_tmpl_id', 'tracking', 'write_date', 'available_in_pos', 'attribute_line_ids'],
            order: _.map(['sequence', 'default_code', 'name'], function (name) {
                return {name: name};
            }),
            condition: function (self) {
                return self.reward_product_ids && self.reward_product_ids.length > 0
            },
            domain: function (self) {
                return [['id', 'in', self.reward_product_ids]];
            },
            context: function (self) {
                return {display_default_code: false};
            },
            loaded: function (self, products) {
                var using_company_currency = self.config.currency_id[0] === self.company.currency_id[0];
                var conversion_rate = self.currency.rate / self.company_currency.rate;
                self.db.add_products(_.map(products, function (product) {
                    if (!using_company_currency) {
                        product.lst_price = round_pr(product.lst_price * conversion_rate, self.currency.rounding);
                    }
                    product.categ = _.findWhere(self.product_categories, {'id': product.categ_id[0]});
                    product.pos = self;
                    return new models.Product({}, product);
                }));
            },
        }
    ]);

    var _super_Orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        init_from_JSON: function (json) {
            var res = _super_Orderline.init_from_JSON.apply(this, arguments);
            if (json.coupon_program_id) {
                this.coupon_program_id = json.coupon_program_id
            }
            if (json.coupon_program_name) {
                this.coupon_program_name = json.coupon_program_name
            }
            if (json.coupon_id) {
                this.coupon_id = json.coupon_id
            }
            if (json.coupon_code) {
                this.coupon_code = json.coupon_code
            }
            return res;
        },
        export_as_JSON: function () {
            var json = _super_Orderline.export_as_JSON.apply(this, arguments);
            if (this.coupon_program_id) {
                json.coupon_program_id = this.coupon_program_id
            }
            if (this.coupon_program_name) {
                json.coupon_program_name = this.coupon_program_name
            }
            if (this.coupon_id) {
                json.coupon_id = this.coupon_id
            }
            if (this.coupon_code) {
                json.coupon_code = this.coupon_code
            }
            return json;
        },
        export_for_printing: function () {
            var receipt_line = _super_Orderline.export_for_printing.apply(this, arguments);
            receipt_line['coupon_code'] = null;
            receipt_line['coupon_program_name'] = null;
            if (this.coupon_code) {
                receipt_line.coupon_code = this.coupon_code;
            }
            if (this.coupon_program_name) {
                receipt_line.coupon_program_name = this.coupon_program_name;
            }
            return receipt_line;
        },
        can_be_merged_with: function (orderline) {
            var merge = _super_Orderline.can_be_merged_with.apply(this, arguments);
            if (this.coupon_id || this.coupon_program_id) {
                return false;
            }
            return merge
        },
        set_quantity: function (quantity, keep_price) {
            _super_Orderline.set_quantity.apply(this, arguments);
        }
    });

    var _super_PosModel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        async automaticSetCoupon() {
            const selectedOrder = this.get_order();
            let lineAppliedCoupon = selectedOrder.orderlines.models.find(l => l.coupon_program_id != undefined)
            if (this.couponProgramsAutomatic && !lineAppliedCoupon) {
                this._autoRemoveCouponLines()
                for (let i = 0; i < this.couponProgramsAutomatic.length; i++) {
                    let couponProgram = this.couponProgramsAutomatic[i];
                    let rule = this.couponRule_by_id[couponProgram.rule_id[0]]
                    let reward = this.couponReward_by_id[couponProgram.reward_id[0]]
                    let canBeApplyCoupon = await this._checkCouponRule(couponProgram, null, rule, reward, true)
                    if (canBeApplyCoupon) {
                        let hasAppliedCoupon = this._applyCouponReward(couponProgram, null, rule, reward);
                        if (hasAppliedCoupon) {
                            this.chrome.showPopup('ConfirmPopup', {
                                title: this.env._t('Successfully'),
                                body: this.env._t('Promotion/Coupon: ') + couponProgram.name + this.env._t(' Applied to Oder')
                            })
                        }
                    }
                }
            }
        },

        _autoRemoveCouponLines() {
            const selectedOrder = this.get_order();
            selectedOrder.orderlines.models.forEach(l => {
                if (l.coupon_program_id) {
                    selectedOrder.remove_orderline(l)
                }
            })
            selectedOrder.orderlines.models.forEach(l => {
                if (l.coupon_program_id) {
                    selectedOrder.remove_orderline(l)
                }
            })
            selectedOrder.orderlines.models.forEach(l => {
                if (l.coupon_program_id) {
                    selectedOrder.remove_orderline(l)
                }
            })
        },
        _applyCouponReward(program, coupon, rule, reward) {
            const selectedOrder = this.get_order();
            const product = this.db.get_product_by_id(reward.discount_line_product_id[0])
            if (!product) {
                return this.chrome.showPopup('ErrorPopup', {
                    title: this.env._t('Warning'),
                    body: this.env._t('Please set available in POS for product: ') + reward.discount_line_product_id[1]
                })
            }
            let appliedRewardSuccessfully = false;
            if (reward.reward_type == 'discount') { // discount
                let price = 0;
                if (reward.discount_apply_on == 'on_order') { // discount apply on order
                    if (reward.discount_type == 'percentage') {
                        price = selectedOrder.get_total_with_tax() / 100 * reward.discount_percentage
                    } else {
                        price = reward.discount_fixed_amount
                    }
                    if (price > 0 && reward.discount_max_amount > 0 && price > reward.discount_max_amount) {
                        price = reward.discount_max_amount
                    }
                }
                if (reward.discount_apply_on == 'cheapest_product') { // discount apply on cheapest
                    let lineCheapest;
                    selectedOrder.orderlines.models.forEach(l => {
                        if (!lineCheapest || (lineCheapest && lineCheapest.get_price_with_tax() >= l.get_price_with_tax())) {
                            lineCheapest = l
                        }
                    })
                    if (reward.discount_type == 'percentage') {
                        price = lineCheapest.get_price_with_tax() / 100 * reward.discount_percentage
                    } else {
                        price = reward.discount_fixed_amount
                    }
                    if (price > 0 && reward.discount_max_amount > 0 && price > reward.discount_max_amount) {
                        price = reward.discount_max_amount
                    }
                }
                if (reward.discount_apply_on == 'specific_products') { // discount apply on specific products
                    selectedOrder.orderlines.models.forEach(l => {
                        if (reward.discount_specific_product_ids.includes(l.product.id)) {
                            price += l.get_price_with_tax()
                        }
                    })
                    if (reward.discount_type == 'percentage') {
                        price = price / 100 * reward.discount_percentage
                    } else {
                        price = reward.discount_fixed_amount
                    }
                    if (price > 0 && reward.discount_max_amount > 0 && price > reward.discount_max_amount) {
                        price = reward.discount_max_amount
                    }
                }
                var line = new models.Orderline({}, {
                    pos: this,
                    order: selectedOrder,
                    product: product
                });
                if (coupon) {
                    line.coupon_id = coupon.id
                    line.coupon_code = coupon.code
                }
                line.coupon_program_id = program.id
                line.coupon_program_name = program.name;
                line.price_manually_set = true; //no need pricelist change, price of promotion change the same, i blocked
                line.set_quantity(-1);
                line.set_unit_price(price);
                selectedOrder.orderlines.add(line);
                selectedOrder.trigger('change', selectedOrder)
                appliedRewardSuccessfully = true;
            } else { // free product
                const reward_product = this.db.get_product_by_id(reward.reward_product_id[0])
                let totalProductsMatchedRuleInCart = 0;
                selectedOrder.orderlines.models.forEach(l => {
                    if (rule.applied_product_ids.includes(l.product.id)) {
                        totalProductsMatchedRuleInCart += l.quantity
                    }
                })
                if (totalProductsMatchedRuleInCart >= rule.rule_min_quantity) {
                    let min_qty = rule.rule_min_quantity || 1
                    let quantity_free = parseInt(totalProductsMatchedRuleInCart / min_qty * reward.reward_product_quantity);
                    var line = new models.Orderline({}, {
                        pos: this,
                        order: selectedOrder,
                        product: reward_product
                    });
                    if (coupon) {
                        line.coupon_id = coupon.id
                        line.coupon_code = coupon.code
                    }
                    line.coupon_program_id = program.id
                    line.coupon_program_name = program.name
                    line.price_manually_set = true; //no need pricelist change, price of promotion change the same, i blocked
                    line.set_quantity(quantity_free);
                    line.set_unit_price(0);
                    selectedOrder.orderlines.add(line);
                    selectedOrder.trigger('change', selectedOrder)
                    appliedRewardSuccessfully = true
                }
            }
            return appliedRewardSuccessfully
        },

        async _checkCouponRule(program, coupon, rule, reward, automaticApplied) {
            const rewardDroduct = this.db.get_product_by_id(reward.reward_product_id[0])
            const productDiscount = this.db.get_product_by_id(reward.discount_line_product_id[0])
            if (!rewardDroduct && reward.reward_type != 'discount') {
                await this.rpc({
                    model: 'product.product',
                    method: 'write',
                    args: [[reward.reward_product_id[0]], {
                        'available_in_pos': true
                    }],
                    context: {}
                })
                this.chrome.showPopup('ErrorPopup', {
                    title: this.env._t('Error'),
                    body: this.env._t('Please set available in POS for product: ') + reward.reward_product_id[1]
                })
                return false
            }
            if (!productDiscount && reward.reward_type == 'discount') {
                await this.rpc({
                    model: 'product.product',
                    method: 'write',
                    args: [[reward.discount_line_product_id[0]], {
                        'available_in_pos': true
                    }],
                    context: {}
                })
                this.chrome.showPopup('ErrorPopup', {
                    title: this.env._t('Error'),
                    body: this.env._t('Please set available in POS for product: ') + reward.discount_line_product_id[1]
                })
                return false
            }
            const selectedOrder = this.get_order()
            let client = selectedOrder.get_client()
            const currentTime = new Date().getTime()
            const productIdsInCart = selectedOrder.orderlines.models.map(l => l.product.id)
            const productIdsOfRuleExistInCart = rule.applied_product_ids.filter(product_id => productIdsInCart.includes(product_id) == true)
            let errorMessage;
            let couponPrograms = await this.rpc({
                model: 'coupon.program',
                method: 'search_read',
                domain: [['id', '=', program.id]],
                fields: ['pos_order_count', 'active'],
            })
            let totalAmountCompare = selectedOrder.get_total_with_tax();
            let totalTax = selectedOrder.get_total_tax();
            if (rule.rule_minimum_amount_tax_inclusion == "tax_excluded") {
                totalAmountCompare -= totalTax
            }
            if (rule.rule_minimum_amount > 0 && rule.rule_minimum_amount >= totalAmountCompare) {
                errorMessage = this.env._t('Promotion/Coupon have Minimum Purchase Amount Total of Order required bigger than ' + this.format_currency(rule.rule_minimum_amount))
                if (!automaticApplied) {
                    this.chrome.showPopup('ErrorPopup', {
                        title: this.env._t('Warning'),
                        body: errorMessage
                    })
                }
                return false
            }
            if (rule.rule_min_quantity > 0) {
                let totalProductsMatchedRuleInCart = 0;
                selectedOrder.orderlines.models.forEach(l => {
                    if (rule.applied_product_ids.includes(l.product.id)) {
                        totalProductsMatchedRuleInCart += l.quantity
                    }
                })
                if (totalProductsMatchedRuleInCart < rule.rule_min_quantity) {
                    errorMessage = this.env._t('Products add to cart not matching with Products condition of Promotion. Minimum quantity is ' + rule.rule_min_quantity)
                    if (!automaticApplied) {
                        this.chrome.showPopup('ErrorPopup', {
                            title: this.env._t('Warning'),
                            body: errorMessage
                        })
                    }
                    return false
                }
            }
            if (coupon) {
                let coupons = await this.rpc({
                    model: 'coupon.coupon',
                    method: 'search_read',
                    domain: [['id', '=', coupon.id]],
                    fields: ['state', 'expiration_date'],
                })
                if (coupons.length == 0 || (coupons.length > 0 && !['new', 'sent'].includes(coupons[0]['state'])) || (coupons.length > 0 && new Date(coupons[0].expiration_date).getTime() < currentTime)) {
                    errorMessage = this.env._t('Coupon is expired or used before')
                    if (!automaticApplied) {
                        this.chrome.showPopup('ErrorPopup', {
                            title: this.env._t('Warning'),
                            body: errorMessage
                        })
                    }
                    return false
                }
            }
            if (rule.rule_date_from && new Date(rule.rule_date_from).getTime() > currentTime) {
                errorMessage = this.env._t('Start Date of Promotion/Coupon is: ') + rule.rule_date_from + this.env._t(' . Bigger than current Date Time')
                if (!automaticApplied) {
                    this.chrome.showPopup('ErrorPopup', {
                        title: this.env._t('Warning'),
                        body: errorMessage
                    })
                }
                return false
            }
            if (rule.rule_date_to && new Date(rule.rule_date_to).getTime() < currentTime) {
                errorMessage = this.env._t('Promotion/Coupon Program is Expired at: ' + rule.rule_date_to)
                if (!automaticApplied) {
                    this.chrome.showPopup('ErrorPopup', {
                        title: this.env._t('Warning'),
                        body: errorMessage
                    })
                }
                return false
            }
            if (program.program_type == 'promotion_program') {  // if promotion program, we required set client
                if (!client && rule.applied_partner_ids.length > 0) {
                    const {confirmed, payload: newClient} = await this.chrome.showTempScreen(
                        'ClientListScreen',
                        {client: null}
                    );
                    if (confirmed) {
                        selectedOrder.set_client(newClient);
                        client = newClient
                    } else {
                        errorMessage = this.env._t('Customer is required')
                        if (!automaticApplied) {
                            this.chrome.showPopup('ErrorPopup', {
                                title: this.env._t('Warning'),
                                body: errorMessage
                            })
                        }
                        return false
                    }
                }
                if (rule.applied_partner_ids.length > 0 && !rule.applied_partner_ids.includes(client.id)) {
                    errorMessage = client.display_name + this.env._t(' not inside Based on Customers of Promotion/Coupon')
                    if (!automaticApplied) {
                        this.chrome.showPopup('ErrorPopup', {
                            title: this.env._t('Warning'),
                            body: errorMessage
                        })
                    }
                    return false
                }
            }
            if (!productIdsInCart) {
                errorMessage = this.env._t('Your cart is blank')
                if (!automaticApplied) {
                    this.chrome.showPopup('ErrorPopup', {
                        title: this.env._t('Warning'),
                        body: errorMessage
                    })
                }
                return false
            }
            if (productIdsOfRuleExistInCart.length == 0 && rule.applied_product_ids.length != 0) {
                errorMessage = this.env._t('Products in cart not matching with Based on Products of Promotion/Coupon')
                if (!automaticApplied) {
                    this.chrome.showPopup('ErrorPopup', {
                        title: this.env._t('Warning'),
                        body: errorMessage
                    })
                }
                return false
            }
            if (program.maximum_use_number > 0) {
                if ((couponPrograms && couponPrograms['0']['pos_order_count'] >= program.maximum_use_number) || (couponPrograms && couponPrograms[0] && !couponPrograms[0]['active'])) {
                    errorMessage = this.env._t('Promotion/Coupon applied full ') + program.maximum_use_number + this.env._t(' POS Orders.')
                    if (!automaticApplied) {
                        this.chrome.showPopup('ErrorPopup', {
                            title: this.env._t('Warning'),
                            body: errorMessage
                        })
                    }
                    return false
                }
            }
            return true
        },

        async getInformationCouponPromotionOfCode(code) {
            let program = this.couponProgram_by_code[code];
            this._autoRemoveCouponLines()
            let coupon;
            let rule;
            let reward;
            if (program) {
                rule = this.couponRule_by_id[program.rule_id[0]]
                reward = this.couponReward_by_id[program.reward_id[0]]
            } else {
                coupon = this.coupon_by_code[code]
                if (coupon) {
                    program = this.couponProgram_by_id[coupon.program_id[0]]
                    rule = this.couponRule_by_id[program.rule_id[0]]
                    reward = this.couponReward_by_id[program.reward_id[0]]
                }

            }
            if (!program && !coupon) {
                this.chrome.showPopup('ErrorPopup', {
                    title: this.env._t('Error'),
                    body: this.env._t(' Coupon is not found. This coupon does not exist or expired or used before')
                })
                return false
            }
            if (program && rule && reward) {
                let canBeApplyCoupon = await this._checkCouponRule(program, coupon, rule, reward)
                if (canBeApplyCoupon) {
                    let hasAppliedCoupon = this._applyCouponReward(program, coupon, rule, reward);
                    if (hasAppliedCoupon) {
                        this.chrome.showPopup('ConfirmPopup', {
                            title: this.env._t('Successfully'),
                            body: this.env._t('Promotion/Coupon applied: ') + program.name,
                        })
                        return true
                    }
                }
            }
            return false
        },

        async scan_product(parsed_code) {
            console.log('-> scan barcode: ' + parsed_code.code);
            const barcodeScanned = parsed_code.code
            const resultOfCore = _super_PosModel.scan_product.apply(this, arguments);
            if (!resultOfCore) {
                const scanCoupon = this.getInformationCouponPromotionOfCode(barcodeScanned)
                if (!scanCoupon) {
                    this.chrome.showPopup('ErrorPopup', {
                        title: this.env._t('Unknow Barcode'),
                        body: this.env._t('We not found any item with barcode: ' + barcodeScanned)
                    })
                }

            }
            return resultOfCore
        },
    })
});