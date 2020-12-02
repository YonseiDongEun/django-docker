async function fetch_json(loc){
    var res = await fetch(loc);
    if(res.ok)
        return await res.json();
    else
        return null;
}

function to_table_row(arr){
    var r=document.createElement("tr")
    for(var i =0;i<arr.length;i++){
        var d=document.createElement("td")
        d.innerText = arr[i];
        r.append(d);
    }
    return r;
}