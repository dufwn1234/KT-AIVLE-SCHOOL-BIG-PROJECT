// 다른 페이지에서 'callEvent' 이벤트를 감지하여 동작 수행
document.addEventListener('callEvent', function(event) {
    const userToCall = event.detail.userToCall;
    // const mouseX = event.detail.mouseX;
    // const mouseY = event.detail.mouseY;
    // 말풍선과 이미지를 표시하는 함수 호출
    showSpeechBubbleAndImage();
  });