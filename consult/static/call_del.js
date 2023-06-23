'use strict';

const baseURL = "/"

let localAudio = document.querySelector('#localAudio');
let remoteAudio = document.querySelector('#remoteAudio');

let otherUser;
let remoteRTCMessage;

let iceCandidatesFromCaller = [];
let peerConnection;
let remoteStream;
let localStream;

let callInProgress = false;

//event from html
function call() {
    let userToCall = document.getElementById("callName").value;
    otherUser = userToCall;

    // beReady()
    //     .then(bool => {
    //         processCall(userToCall)
    //     })

//     // 전화를 거는 대상자가 로그인 상태인지 확인하는 로직 추가
//   if (isUserLoggedIn(userToCall)) {
    beReady()
      .then(bool => {
        processCall(userToCall);
        // 'callEvent' 이벤트를 발생시키고 전달할 데이터를 설정
        const callEventData = {
          userToCall: userToCall
        };
        const callEvent = new CustomEvent('callEvent', { detail: callEventData });
        document.dispatchEvent(callEvent);
      });
//   }
}

// // 대상자의 마우스 위치에 말풍선과 이미지를 표시하는 함수
// function showSpeechBubbleAndImage(x, y) {
//     const speechBubble = document.createElement("div");
//     speechBubble.classList.add("speech-bubble");
//     speechBubble.innerHTML = "<p>전화가 왔어요!</p>";
//     speechBubble.style.left = x + "px";
//     speechBubble.style.top = y + "px";
//     document.body.appendChild(speechBubble);
  
//     const image = document.createElement("img");
//     image.src = "https://cdn.pixabay.com/photo/2015/11/06/13/13/call-center-1027585_1280.jpg";
//     image.alt = "말풍선과 이미지";
//     image.width = 80;
//     image.height = 80;
//     document.body.appendChild(image);

// 대상자의 말풍선과 이미지를 오른쪽 하단에 표시하는 함수
function showSpeechBubbleAndImage() {
    const speechBubble = document.createElement("div");
    speechBubble.classList.add("speech-bubble");
    speechBubble.innerHTML = "<p>전화가 왔어요!</p>";
    speechBubble.style.right = "10px";
    speechBubble.style.bottom = "10px";
    document.body.appendChild(speechBubble);
  
    const image = document.createElement("img");
    image.src = "https://cdn.pixabay.com/photo/2015/11/06/13/13/call-center-1027585_1280.jpg";
    image.alt = "말풍선과 이미지";
    image.width = 80;
    image.height = 80;
    document.body.appendChild(image);
  
    // 전화를 받은 후 말풍선과 이미지를 제거하는 함수
    function removeSpeechBubbleAndImage() {
      document.body.removeChild(speechBubble);
      document.body.removeChild(image);
      document.removeEventListener("click", answer);
    }
  
    // 전화를 받는 동작 실행 시 말풍선과 이미지를 제거하는 함수를 호출
    setTimeout(removeSpeechBubbleAndImage, 5000); // 예시로 5초 후에 제거하도록 설정
  }

//event from html
function answer() {
    //do the event firing

    beReady()
        .then(bool => {
            processAccept();
        })

    document.getElementById("answer").style.display = "none";
}

let pcConfig = {
    "iceServers":
        [
            { "url": "stun:stun.jap.bloggernepal.com:5349" },
            {
                "url": "turn:turn.jap.bloggernepal.com:5349",
                "username": "guest",
                "credential": "somepassword"
            },
            {"url": "stun:stun.l.google.com:19302"}
        ]
};

// Set up audio and video regardless of what devices are present.
let sdpConstraints = {
    offerToReceiveAudio: true,
    // offerToReceiveVideo: true
};

/////////////////////////////////////////////

let socket;
let callSocket;
function connectSocket() {
    let ws_scheme = window.location.protocol == "https:" ? "wss://" : "ws://";
    console.log(ws_scheme);

    callSocket = new WebSocket(
        ws_scheme
        + window.location.host
        + '/ws/call/'
    );

    callSocket.onopen = event =>{
    //let's send myName to the socket
        callSocket.send(JSON.stringify({
            type: 'login',
            data: {
                name: myName
            }
        }));
    }

    callSocket.onmessage = (e) =>{
        let response = JSON.parse(e.data);

        // console.log(response);

        let type = response.type;

        if(type == 'connection') {
            console.log(response.data.message)
        }

        if(type == 'call_received') {
            // console.log(response);
            onNewCall(response.data)
        }

        if(type == 'call_answered') {
            onCallAnswered(response.data);
        }

        if(type == 'ICEcandidate') {
            onICECandidate(response.data);
        }
    }

    const onNewCall = (data) =>{
        //when other called you
        //show answer button

        otherUser = data.caller;
        remoteRTCMessage = data.rtcMessage

        // document.getElementById("profileImageA").src = baseURL + callerProfile.image;
        document.getElementById("callerName").innerHTML = otherUser;
        document.getElementById("call").style.display = "none";
        document.getElementById("answer").style.display = "block";
    }

    const onCallAnswered = (data) =>{
        //when other accept our call
        remoteRTCMessage = data.rtcMessage
        peerConnection.setRemoteDescription(new RTCSessionDescription(remoteRTCMessage));

        document.getElementById("calling").style.display = "none";

        console.log("Call Started. They Answered");
        // console.log(pc);

        callProgress()
    }

    const onICECandidate = (data) =>{
        // console.log(data);
        console.log("GOT ICE candidate");

        let message = data.rtcMessage

        let candidate = new RTCIceCandidate({
            sdpMLineIndex: message.label,
            candidate: message.candidate
        });

        if (peerConnection) {
            console.log("ICE candidate Added");
            peerConnection.addIceCandidate(candidate);
        } else {
            console.log("ICE candidate Pushed");
            iceCandidatesFromCaller.push(candidate);
        }

    }

}

/**
 * 
 * @param {Object} data 
 * @param {number} data.name - the name of the user to call
 * @param {Object} data.rtcMessage - the rtc create offer object
 */
function sendCall(data) {
    //to send a call
    console.log("Send Call");

    // socket.emit("call", data);
    callSocket.send(JSON.stringify({
        type: 'call',
        data
    }));

    document.getElementById("call").style.display = "none";
    // document.getElementById("profileImageCA").src = baseURL + otherUserProfile.image;
    document.getElementById("otherUserNameCA").innerHTML = otherUser;
    document.getElementById("calling").style.display = "block";
}



/**
 * 
 * @param {Object} data 
 * @param {number} data.caller - the caller name
 * @param {Object} data.rtcMessage - answer rtc sessionDescription object
 */
function answerCall(data) {
    //to answer a call
    // socket.emit("answerCall", data);
    callSocket.send(JSON.stringify({
        type: 'answer_call',
        data
    }));
    callProgress();
}

/**
 * 
 * @param {Object} data 
 * @param {number} data.user - the other user //either callee or caller 
 * @param {Object} data.rtcMessage - iceCandidate data 
 */
function sendICEcandidate(data) {
    //send only if we have caller, else no need to
    console.log("Send ICE candidate");
    // socket.emit("ICEcandidate", data)
    callSocket.send(JSON.stringify({
        type: 'ICEcandidate',
        data
    }));

}

function beReady() {
    return navigator.mediaDevices.getUserMedia({
        audio: true,
        // video: true
    })
        .then(stream => {
            localStream = stream;
            localAudio.srcObject = stream;

            return createConnectionAndAddStream()
        })
        .catch(function (e) {
            alert('getUserMedia() error: ' + e.name);
        });
}

function createConnectionAndAddStream() {
    createPeerConnection();
    peerConnection.addStream(localStream);
    return true;
}

function processCall(userName) {
    peerConnection.createOffer((sessionDescription) => {
        peerConnection.setLocalDescription(sessionDescription);
        sendCall({
            name: userName,
            rtcMessage: sessionDescription
        })
    }, (error) => {
        console.log("Error");
    });
}

function processAccept() {

    peerConnection.setRemoteDescription(new RTCSessionDescription(remoteRTCMessage));
    peerConnection.createAnswer((sessionDescription) => {
        peerConnection.setLocalDescription(sessionDescription);

        if (iceCandidatesFromCaller.length > 0) {
            //I am having issues with call not being processed in real world (internet, not local)
            //so I will push iceCandidates I received after the call arrived, push it and, once we accept
            //add it as ice candidate
            //if the offer rtc message contains all thes ICE candidates we can ingore this.
            for (let i = 0; i < iceCandidatesFromCaller.length; i++) {
                //
                let candidate = iceCandidatesFromCaller[i];
                console.log("ICE candidate Added From queue");
                try {
                    peerConnection.addIceCandidate(candidate).then(done => {
                        console.log(done);
                    }).catch(error => {
                        console.log(error);
                    })
                } catch (error) {
                    console.log(error);
                }
            }
            iceCandidatesFromCaller = [];
            console.log("ICE candidate queue cleared");
        } else {
            console.log("NO Ice candidate in queue");
        }

        answerCall({
            caller: otherUser,
            rtcMessage: sessionDescription
        })

    }, (error) => {
        console.log("Error");
    })
}

/////////////////////////////////////////////////////////

function createPeerConnection() {
    try {
        peerConnection = new RTCPeerConnection(pcConfig);
        // peerConnection = new RTCPeerConnection();
        peerConnection.onicecandidate = handleIceCandidate;
        peerConnection.onaddstream = handleRemoteStreamAdded;
        peerConnection.onremovestream = handleRemoteStreamRemoved;
        console.log('Created RTCPeerConnnection');
        return;
    } catch (e) {
        console.log('Failed to create PeerConnection, exception: ' + e.message);
        alert('Cannot create RTCPeerConnection object.');
        return;
    }
}

function handleIceCandidate(event) {
    // console.log('icecandidate event: ', event);
    if (event.candidate) {
        console.log("Local ICE candidate");
        // console.log(event.candidate.candidate);

        sendICEcandidate({
            user: otherUser,
            rtcMessage: {
                label: event.candidate.sdpMLineIndex,
                id: event.candidate.sdpMid,
                candidate: event.candidate.candidate
            }
        })

    } else {
        console.log('End of candidates.');
    }
}

function handleRemoteStreamAdded(event) {
    console.log('Remote stream added.');
    remoteStream = event.stream;
    remoteAudio.srcObject = remoteStream;
}

function handleRemoteStreamRemoved(event) {
    console.log('Remote stream removed. Event: ', event);
    remoteAudio.srcObject = null;
    localAudio.srcObject = null;
}

window.onbeforeunload = function () {
    if (callInProgress) {
        stop();
    }
};


function stop() {
    localStream.getTracks().forEach(track => track.stop());
    callInProgress = false;
    peerConnection.close();
    peerConnection = null;
    document.getElementById("call").style.display = "block";
    document.getElementById("answer").style.display = "none";
    document.getElementById("inCall").style.display = "none";
    document.getElementById("calling").style.display = "none";
    document.getElementById("endAudioButton").style.display = "none"
    otherUser = null;
    window.location.href = '/survey/';
}

function callProgress() {

    document.getElementById("audios").style.display = "block";
    document.getElementById("otherUserNameC").innerHTML = otherUser;
    document.getElementById("inCall").style.display = "block";

    callInProgress = true;
}


var start_Time = new Date();

function updateCallDuration() {
    var currentTime = new Date();
    var timeDifference = currentTime - start_Time;
    var seconds = Math.floor(timeDifference / 1000);
    var minutes = Math.floor(seconds / 60);
    var hours = Math.floor(minutes / 60);
    seconds %= 60;
    minutes %= 60;

    var durationString = hours.toString().padStart(2, '0') + ':' +
                         minutes.toString().padStart(2, '0') + ':' +
                         seconds.toString().padStart(2, '0');

    document.getElementById("callDuration").textContent = "Call Duration: " + durationString;
}

setInterval(updateCallDuration, 1000);