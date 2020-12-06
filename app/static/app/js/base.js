validation_failed= function(errs){
    var al = $("#alert_msg");
    var st = document.createElement("strong");
    st.innerText = "Validation Failed"
    var ul = document.createElement("ul");
    for(e of errs){
        var li = document.createElement("li");
        li.innerText = e
        ul.append(li)
    }
    al.removeClass("hide")
    al.text("")
    al.append(st)
    al.append(ul)
}