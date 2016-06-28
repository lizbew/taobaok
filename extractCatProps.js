(function extractCatProps() {
	var cateId = document.querySelector('input#SelectCategoryID').getAttribute('value');
    var catProps = [];
    var ul = document.querySelector('#J_module-property > div.skin > ul');

	function cut_label_text(txt){
		var i = txt.lastIndexOf('：');
		if (i > 0){
			return txt.substring(0, i);
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
            key: k,
            cat: 'keySpus',
            text: t,
        };
        catProps.push(data);
    });

    var spus_list = ul.querySelectorAll('li[name="spus"]');
    spus_list.forEach(function(spus) {
        var lb = spus.querySelector('label:first-child');
        var k = lb.getAttribute('id');
        var t = cut_label_text(lb.innerText);
        var data = {
            cat: 'spus',
            text: t
        };

        if (!!k) {
            var j = k.lastIndexOf('-');
            if (j > 0) {
                k = k.substring(j + 1);
            }
            data['key'] = k;
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
            data['key'] = k;
            var checkbox_list = spus.querySelectorAll('input#' + k);
            var ops = [];
            checkbox_list.forEach(function(ckbx) {
                var v = ckbx.getAttribute('value');
                var vt = ckbx.nextSibling.innerText;
                ops.push([v, vt]);
            });
            data['options'] = ops;
            data['select_mode'] = 'multi';
        }
        catProps.push(data);
    });
    //return catProps;
	console.log('cateId: ' + cateId);
	console.log(JSON.stringify(catProps));
})();