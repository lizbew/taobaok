(function extractCatProps() {
	var cateId = document.querySelector('input#SelectCategoryID').getAttribute('value');
    var cateName = document.querySelector('#product-info li:first-of-type').innerText;
    var catProps = [];
    var colorMap = {};
    var sizeTypeMap = {};

    var ul = document.querySelector('#J_module-property > div.skin > ul');

	function cut_label_text(txt){
		var i = txt.lastIndexOf('：');
		if (i > 0){
			return txt.substring(0, i);
		}
		return txt;
	}

    function cut_prop_id(txt) {
        var i = txt.lastIndexOf('_');
        if (i > 0) {
            return txt.substring(i+1);
        }
        return txt;
    }
	
    var keySpus_list = ul.querySelectorAll('li[name="keySpus"]');
    keySpus_list.forEach(function(keySpus) {
        var lb = keySpus.querySelector('label:first-child');
        var k = lb.getAttribute('for');
        var t = cut_label_text(lb.innerText);
        //var options = keySpus.querySelectorAll('select#' + k + ' > option');
        var data = {
            key: cut_prop_id(k),
            kind: 'keySpus',
            label: t,
        };
        catProps.push(data);
    });

    var spus_list = ul.querySelectorAll('li[name="spus"]');
    spus_list.forEach(function(spus) {
        var lb = spus.querySelector('label:first-child');
        var k = lb.getAttribute('id');
        var t = cut_label_text(lb.innerText);
        var data = {
            kind: 'spus',
            label: t
        };

        if (!!k) {
            var j = k.lastIndexOf('-');
            if (j > 0) {
                k = k.substring(j + 1);
            }
            data['key'] = cut_prop_id(k);
            var options = spus.querySelectorAll('select#' + k + ' > option');
            if (!!options) {
                var ops = [];
                options.forEach(function(opt) {
                    var ov = opt.getAttribute('value');
                    var ot = opt.innerText;
                    if (!!ov) {
                        ops.push([ov, ot]);
                    }
                });
                data['options'] = ops;
                data['select_mode'] = 'single';
            }

        } else {
            //for checkbox
            k = spus.getAttribute('id').replace('spu', 'prop');
            data['key'] = cut_prop_id(k);
            var checkbox_list = spus.querySelectorAll('input#' + k);
            var ops = [];
            checkbox_list.forEach(function(ckbx) {
                var v = ckbx.getAttribute('value');
                var vt = ckbx.nextElementSibling.innerText;
                ops.push([v, vt]);
            });
            data['options'] = ops;
            data['select_mode'] = 'multi';
        }
        catProps.push(data);
    });

    // colorMap
    document.querySelectorAll('#sku-color-tab-contents label input').forEach(function(e){
        var v = e.getAttribute('value');
        var t = e.getAttribute('data-text');
        colorMap[v] = t;
    });

    //sizeTypeMap
    document.querySelectorAll('div.sku-size-wrap li.sku-item input.J_Checkbox').forEach(function(e){
        var v = e.getAttribute('value'); 
        var t = e.nextElementSibling.getAttribute('title');
        sizeTypeMap[v] = t;
    });

    //return catProps;
    var data = {
        cateId: cateId,
        cateName: cateName, 
        catProps: catProps,
        colorMap: colorMap,
        sizeTypeMap: sizeTypeMap
    };
	console.log('cateId: ' + cateId);
	console.log(JSON.stringify(data));
})();