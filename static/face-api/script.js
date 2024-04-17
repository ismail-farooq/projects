document.addEventListener('DOMContentLoaded', () => {
  const video = document.getElementById('video');

  Promise.all([
    faceapi.nets.tinyFaceDetector.loadFromUri('../static/face-api/models'),
    faceapi.nets.faceLandmark68Net.loadFromUri('../static/face-api/models'),
    faceapi.nets.faceRecognitionNet.loadFromUri('../static/face-api/models'),
    faceapi.nets.faceExpressionNet.loadFromUri('../static/face-api/models')
  ]).then(startVideo);

  navigator.getUserMedia = ( navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia || navigator.mediaDevices.getUserMedia);

  function startVideo() {
    navigator.getUserMedia(
      { video: {} },
      stream => video.srcObject = stream,
      err => console.error(err)      
    );
  }

  video.addEventListener('play', () => {
    const canvas = faceapi.createCanvasFromMedia(video);
    document.body.append(canvas);
    const displaySize = { width: video.width, height: video.height };
    faceapi.matchDimensions(canvas, displaySize);
    setInterval(async () => {
      const detections = await faceapi.detectAllFaces(video, new faceapi.TinyFaceDetectorOptions()).withFaceLandmarks().withFaceExpressions();
      const resizedDetections = faceapi.resizeResults(detections, displaySize);
      canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);
      faceapi.draw.drawDetections(canvas, resizedDetections);
      faceapi.draw.drawFaceLandmarks(canvas, resizedDetections);
      faceapi.draw.drawFaceExpressions(canvas, resizedDetections);

      // Check if faceCountElement exists before updating
      const faceCountElement = document.getElementById('faceCount');
      if (faceCountElement) {
        faceCountElement.innerText = `Number of faces detected: ${resizedDetections.length}`;
      } else {
        console.error('faceCountElement not found');
      }
    }, 100);
  });
});
