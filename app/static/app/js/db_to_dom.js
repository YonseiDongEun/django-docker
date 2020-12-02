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