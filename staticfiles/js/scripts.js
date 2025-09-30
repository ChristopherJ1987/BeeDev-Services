function menu() {
    var x = document.getElementById("myLinks")
    console.log("clicked")
    if(x.style.display === 'flex') {
        x.style.display = 'none'
    } else {
        x.style.display = 'flex'
        x.style.flexDirection = 'column'
        x.style.width = "100%"
    }
}