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

function json_array_as_table(arr, tbl){
    fields = arr[1]

    tbl.innerHTML= ''
    var thd = tbl.createTHead()
    var tbd = tbl.createTBody()

    var r=document.createElement("tr")
    for(var i =0;i<fields.length;i++){
        var d=document.createElement("td")
        var st= document.createElement("strong")
        st.innerText = fields[i];
        d.append(st);
        r.append(d);
    }
    thd.append(r);

    for(var j=2;j<arr.length;j++){
        var r=document.createElement("tr")
        for(var i =0;i<fields.length;i++){
            var d=document.createElement("td")
            d.innerText = arr[j][fields[i]];
            r.append(d);
        }
        tbd.append(r);
    }
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

setup_query_ui = function( api_url, tbl_selector, alert_selector, execute_selector, input_selector, callback){
    do_query = async function(sql_st){
        var query_url = new URL(api_url, window.location.origin)
        var post_data = {sql_st}
        var res = await fetch_json_post(query_url.href, post_data);
        var tbl = $(tbl_selector)[0]
        var success = res[0];
        var alert_dom = $(alert_selector)[0]
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
        json_array_as_table(res, tbl)
        $(tbl_selector).find("td").on("click",callback)
    }
    $(async function(){
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