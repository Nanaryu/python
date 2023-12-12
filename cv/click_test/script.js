var main = document.getElementById("main");
document.addEventListener('click', function(event){
    let x = event.clientX;
    let y = event.clientY;

    // Create a new span element
    let newSpan = document.createElement('span');
    newSpan.style.position = 'absolute';
    newSpan.style.borderRadius = '100%';
    newSpan.style.backgroundColor = 'blueviolet';
    newSpan.style.top = y + 'px';
    newSpan.style.left = x + 'px';
    newSpan.style.width = '5px';
    newSpan.style.height = '5px';
    newSpan.style.color = "blueviolet"
    newSpan.innerHTML = `(${x},${y})`

    // Append the new span element to the main div
    main.appendChild(newSpan);
});
