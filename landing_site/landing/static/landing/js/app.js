function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const csrftoken = getCookie('csrftoken');

const modal = document.getElementById('orderModal');
const openButtons = ['orderTop','orderHero','orderCta'].map(id=>document.getElementById(id));
const closeButtons = [document.getElementById('modalClose'), document.getElementById('cancelBtn')];
const form = document.getElementById('orderForm');
const submitBtn = document.getElementById('submitBtn');
const toast = document.getElementById('toast');

document.getElementById('y').textContent = new Date().getFullYear();

openButtons.forEach(btn=>btn.addEventListener('click',()=>{
  modal.setAttribute('open','');
  document.getElementById('name').focus();
}));
closeButtons.forEach(btn=>btn.addEventListener('click',()=>{
  modal.removeAttribute('open');
  form.reset();
  hideErrors();
}));
modal.addEventListener('click', (e)=>{ if(e.target === modal) closeButtons[0].click(); });

function showToast(text, ok=true){
  toast.textContent = text;
  toast.classList.remove('hidden');
  toast.style.borderColor = ok ? 'rgba(91,228,155,.35)' : 'rgba(255,107,107,.35)';
  setTimeout(()=>toast.classList.add('hidden'), 3500);
}

function hideErrors(){
  document.querySelectorAll('.error').forEach(el=>{ el.classList.add('hidden'); el.textContent=''; });
}

form.addEventListener('submit', async (e)=>{
  e.preventDefault();
  hideErrors();
  submitBtn.disabled = true; submitBtn.textContent = 'Отправляем…';

  const fd = new FormData(form);
  try {
    const res = await fetch('/api/order/', {
      method:'POST',
      body: fd,
      headers: {'X-CSRFToken': csrftoken}
    });
    const data = await res.json();
    if(res.ok && data.ok){
      showToast(data.message || 'Заявка отправлена');
      form.reset();
      modal.removeAttribute('open');
    } else if(data.errors){
      Object.entries(data.errors).forEach(([k,v])=>{
        const errEl = document.querySelector(`.error[data-error-for="${k}"]`);
        if(errEl){ errEl.textContent = v; errEl.classList.remove('hidden'); }
      });
    } else {
      showToast(data.error || 'Произошла ошибка. Попробуйте позже.', false);
    }
  } catch (err){
    console.error(err);
    showToast('Сетевая ошибка. Проверьте подключение.', false);
  } finally {
    submitBtn.disabled = false; submitBtn.textContent = 'Отправить';
  }
});
