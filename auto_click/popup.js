const recordBtn = document.getElementById('recordBtn');
const stopBtn = document.getElementById('stopBtn');
const playBtn = document.getElementById('playBtn');
const loopCount = document.getElementById('loopCount');

chrome.storage.local.get('isRecording', res => {
  if (res.isRecording) {
    recordBtn.style.display = 'none';
    stopBtn.style.display = 'block';
  }
});

recordBtn.onclick = async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  chrome.storage.local.set({ actions: [], isRecording: true });
  chrome.scripting.executeScript({
    target: { tabId: tab.id },
    files: ['content.js']
  });
  recordBtn.style.display = 'none';
  stopBtn.style.display = 'block';
};

stopBtn.onclick = () => {
  chrome.storage.local.set({ isRecording: false });
  recordBtn.style.display = 'block';
  stopBtn.style.display = 'none';
};

playBtn.onclick = async () => {
  const loops = parseInt(loopCount.value) || 1;
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: playbackActions,
    args: [loops]
  });
};

function playbackActions(totalLoops) {
  chrome.storage.local.get('actions', res => {
    const actions = res.actions || [];
    if (!actions.length) return alert('No actions recorded!');

    let loop = 0;
    function runLoop() {
      if (loop >= totalLoops) return;
      let i = 0;
      function next() {
        if (i >= actions.length) {
          loop++;
          setTimeout(runLoop, 800);
          return;
        }
        const a = actions[i];
        const el = document.querySelector(a.selector);
        if (el) {
          if (a.type === 'click') el.click();
          if (a.type === 'input') {
            el.value = a.value;
            el.dispatchEvent(new Event('input', { bubbles: true }));
          }
        }
        i++;
        setTimeout(next, 500);
      }
      next();
    }
    runLoop();
  });
}