async function fetch_json(loc){
    var res = await fetch(loc);
    if(res.ok)
        return await res.json();
    else
        return null;
}
async function fetch_json_post(loc, data){
    var res = await fetch(loc,{
        credentials: "same-origin",
        method:"POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
          },
        body:JSON.stringify(data)
    });
    if(res.ok)
        return await res.json();
    else
        return null;
}

function json_result_as_table(data, tbl){
    fields = data.fields

    tbl.innerHTML= ''
    var thd = tbl.createTHead()
    var tbd = tbl.createTBody()
    
    
    var r=document.createElement("tr")
    for(var i =0;i<fields.length;i++){
        var d=document.createElement("td")
        var st= document.createElement("strong")
        st.innerText = fields[i].fieldname;
        d.append(st);
        r.append(d);
    }
    thd.append(r);
    
    for(var tu of data.tuples){
        var r=document.createElement("tr")
        for(var i =0;i<fields.length;i++){
            var d=document.createElement("td")
            d.innerText = tu[fields[i].fieldname];
            r.append(d);
        }
        tbd.append(r);
    }
    
    if(tbd.children.length==0){
        var tft = tbl.createTFoot()
        var tr = document.createElement("tr")
        var td = document.createElement("td")
        td.colSpan=`${fields.length}`
        td.style.textAlign='center'
        td.style.color='#AAA'
        td.innerText = "(No Data)"
        tr.append(td)
        tft.append(tr)
    }
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

setup_query_ui = function( api_url, tbl_selector, alert_selector, execute_selector, input_selector, callback){
    var do_query = async function(sql_st){
        var query_url = new URL(api_url, window.location.origin)
        var post_data = {sql_st}
        var res = await fetch_json_post(query_url.href, post_data);
        var tbl = $(tbl_selector)[0]
        var success = res.success;
        var alert_dom = $(alert_selector)[0]
        console.log(res)
        if(success){
            alert_dom.style.display="None"
        }
        else{
            var alert_type = document.createElement("strong")
            var alert_desc = ""
            alert_dom.innerHTML=""
            alert_type.innerText = "SQL Query Failed"
            alert_desc = "Not a valid where clause."
            alert_dom.append(alert_type)
            alert_dom.append(" | ")
            alert_dom.append(alert_desc)
            alert_dom.style.display="Block"
        }
        json_result_as_table(res, tbl)
        $(tbl_selector).find("tbody td").on("click",callback)
    }
    var do_download = async function(){
        var rows = []
        var th = $(tbl_selector).find("thead")[0].firstChild.cells;
        var tb = $(tbl_selector).find('tbody')[0].rows;
        var attrs = [...th].map(x=>x.textContent)
        rows.push(attrs)
        rows =[attrs].concat([...tb].map(r=>[...r.cells].map(x=>x.textContent)))
        console.log(rows)
        var csvContent = "data:text/csv;charset=utf-8," + rows.map(e => e.join(",")).join("\n");
        var encodedUri = encodeURI(csvContent);
        var link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", `${location.pathname.replaceAll('/','')+Date.now()}.csv`);
        document.body.appendChild(link);
        link.click();
    }
    $(async function(){
        if(execute_selector[0]=='#'){
            $(execute_selector+'_dl').on('click',function(){
                do_download();
            });
        }
        $(execute_selector).on('click',function(){
            do_query( $(input_selector).val());
        });
        $(input_selector).on('keydown',function(e){
            if(e.keyCode==13)
                do_query( $(input_selector).val());
        });
        do_query("")
    })
}
setup_fields_ui = function( columns, tbody_selector, col_type_selector=null, col_name_selector=null, col_create_selector=null, prefix=""){
    var dom_tbody = $(tbody_selector)[0]
    var valid_identifier_pattern = /^[a-zA-Z_][a-zA-Z_0-9]{0,32}/;
    var callback = null;
    if(col_create_selector){
        callback = function(ev){
            this.remove()
        }
    }
    var add_col = (col)=>{
        var tr = document.createElement("tr")
        var td1 = document.createElement("td")
        var td2 = document.createElement("td")
        td1.innerText = col.fieldtype
        td2.innerText = col.fieldname
        if(callback)
            $(tr).on('click',callback);

            tr.append(td1,td2)
        dom_tbody.append(tr)
    }

    var get_cols = ()=>{
        var cols = []
        for( var r of dom_tbody.children){
            var col = {}
            col.fieldtype = r.cells[0].textContent
            col.fieldname = r.cells[1].textContent
            cols.push(col)
        }
        return cols
    }

    for(var col of columns){
        prefixed = {...col}
        prefixed.fieldname = prefix + prefixed.fieldname
        add_col(prefixed)
    }

    if(col_create_selector ){
        var dom_type = $(col_type_selector)
        var dom_name = $(col_name_selector)
        var dom_create = $(col_create_selector)

        dom_name.on("keydown",function(ev){
            if(ev.keyCode==13)
            dom_create.click()
        });
        dom_create.on("click",(ev)=>{
            var valid_fieldname = valid_identifier_pattern.test(dom_name.val())
            get_cols().forEach((x)=>{
                if(x.fieldname.toLowerCase() == dom_name.val().toLowerCase())
                    valid_fieldname = false
            })
            if(!valid_fieldname)
                return;

            add_col({fieldname:dom_name.val(), fieldtype:dom_type.val()})
            dom_name.val("")
        })
    }

    return get_cols;
}