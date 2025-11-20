function loopThroughArray(arr) {
  let output = document.getElementById('output');
  for (let i = 0; i < arr.length; i++) {
    output.innerHTML += `${arr[i]}\n`;
  }
}