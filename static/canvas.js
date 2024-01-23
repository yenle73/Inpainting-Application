var canvas = document.querySelector('canvas');

canvas.width = 512;
canvas.height = 512;

var c = canvas.getContext('2d');
var radius = 10;
var dragging = false; 

c.strokeStyle = "red";
c.lineWidth = radius*2;


var points = [];

var putPoint = function(e) {
    if (dragging) {
        c.lineTo(e.offsetX, e.offsetY);
        c.stroke();
        c.beginPath(); 
        c.arc(e.offsetX, e.offsetY, radius, 0, Math.PI*2);
        c.fillStyle = "red";
        c.fill()
        c.beginPath();
        c.moveTo(e.offsetX, e.offsetY);

        points.push({ x: e.offsetX, y: e.offsetY });
    }
}

var engage = function() {
    dragging = true;
    putPoint(e);
}

var disengage = function() {
    dragging = false;
    c.beginPath();
}

canvas.addEventListener('mousedown', engage);
canvas.addEventListener('mousemove', putPoint);
canvas.addEventListener('mouseup', disengage);

// Adjust the brush
var setRadius = function(newRadius) {
    if (newRadius < minRad)
        newRadius = minRad;
    else if(newRadius > maxRad)
        newRadius = maxRad;

    radius = newRadius;
    c.strokeStyle = "red";
    c.lineWidth = radius*2;

    radSpan.innerHTML = radius;

}

var minRad = 0.5, maxRad = 100, defaultRad = 20, interval = 5,
radSpan = document.getElementById('radval'),
decRad = document.getElementById('decrad'),
incRad = document.getElementById('incrad');

decRad.addEventListener('click', function(){
    setRadius(radius-interval);
})

incRad.addEventListener('click', function(){
    setRadius(radius+interval);
})

setRadius(defaultRad);

// Work with the image
var img = new Image();

var loadButton = document.getElementById('loadButton');
loadButton.addEventListener('click', loadImage());

function loadImage() {
    // Lấy tham chiếu đến input file
    var fileInput = document.getElementById('fileInput');

    // Đảm bảo người dùng đã chọn một file
    if (fileInput.files.length > 0) {
      // Đọc file hình ảnh
      var file = fileInput.files[0];
      var reader = new FileReader();

      reader.onload = function(e) {
        // Thiết lập nguồn hình ảnh từ dữ liệu đọc được
        img.src = e.target.result;
      };

      // Đọc file dưới dạng Data URL
      reader.readAsDataURL(file);
    }
  }


img.onload = function() {
    // Vẽ hình ảnh lên canvas
    c.drawImage(img, 0, 0, canvas.width, canvas.height);

    canvas.addEventListener('mousedown', function(e) {
        dragging = true;
        putPoint(e);
      });

      canvas.addEventListener('mousemove', function(e) {
        putPoint(e);
      });
  
      canvas.addEventListener('mouseup', function() {
        dragging = false;
        c.beginPath();
      });

  }


// Undo button
var undoButton = document.getElementById('undoButton');

undoButton.addEventListener('click', undo());

function undo() {
    // Xóa bước vẽ cuối cùng từ mảng
    points.pop();

    // Xóa toàn bộ drawingCanvas và vẽ lại từ đầu
    c.clearRect(0, 0, canvas.width, canvas.height);
    c.drawImage(img, 0, 0, canvas.width, canvas.height);
    c.beginPath();

    for (var i = 0; i < points.length; i++) {
      c.lineTo(points[i].x, points[i].y);
      c.stroke();
      c.beginPath();
      c.arc(points[i].x, points[i].y, radius, 0, Math.PI * 2);
      c.fill();
      c.beginPath();
      c.moveTo(points[i].x, points[i].y);
    }
  }

  // Clear button
  var clearButton = document.getElementById('clearButton');

  undoButton.addEventListener('click', clearCanvas());

  function clearCanvas() {
    c.clearRect(0, 0, canvas.width, canvas.height);
    points = [];
    c.drawImage(img, 0, 0, canvas.width, canvas.height);
  }

