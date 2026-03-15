/* ============================================================
   FAMILY TREE WEB APPLICATION — main.js
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {

  /* ─── Hamburger Menu ─────────────────────────────────────── */
  const hamburger = document.querySelector('.navbar__hamburger');
  const navMenu   = document.querySelector('.navbar__nav');

  if (hamburger && navMenu) {
    hamburger.addEventListener('click', () => {
      navMenu.classList.toggle('open');
      const spans = hamburger.querySelectorAll('span');
      const isOpen = navMenu.classList.contains('open');
      if (isOpen) {
        spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
        spans[1].style.opacity   = '0';
        spans[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
      } else {
        spans.forEach(s => { s.style.transform = ''; s.style.opacity = ''; });
      }
    });
    // Close menu when link is clicked
    navMenu.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        navMenu.classList.remove('open');
        hamburger.querySelectorAll('span').forEach(s => { s.style.transform = ''; s.style.opacity = ''; });
      });
    });
  }

  /* ─── Active Nav Link ────────────────────────────────────── */
  const currentPath = window.location.pathname.split('/').pop();
  document.querySelectorAll('.navbar__nav a').forEach(link => {
    const href = link.getAttribute('href');
    if (href === currentPath || (currentPath === '' && href === 'index.html')) {
      link.classList.add('active');
    }
  });

  /* ─── Scroll: Back-to-top & Navbar shadow ────────────────── */
  const btt = document.getElementById('backToTop');
  window.addEventListener('scroll', () => {
    if (btt) {
      btt.classList.toggle('visible', window.scrollY > 400);
    }
  }, { passive: true });

  if (btt) {
    btt.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
  }

  /* ─── Intersection Observer: fade-up ─────────────────────── */
  const fadeEls = document.querySelectorAll('.fade-up');
  if (fadeEls.length) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    fadeEls.forEach(el => observer.observe(el));
  }

  /* ─── Contact Form Validation ────────────────────────────── */
  const form = document.getElementById('contactForm');
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      let valid = true;

      const fields = [
        { id: 'name',    min: 2,   msg: 'Please enter your full name (min 2 characters).' },
        { id: 'email',   type: 'email', msg: 'Please enter a valid email address.' },
        { id: 'subject', min: 4,   msg: 'Subject must be at least 4 characters.' },
        { id: 'message', min: 20,  msg: 'Message must be at least 20 characters.' },
      ];

      fields.forEach(({ id, min, type, msg }) => {
        const input = document.getElementById(id);
        const error = document.getElementById(id + 'Error');
        if (!input || !error) return;

        input.classList.remove('error');
        error.classList.remove('visible');

        const val = input.value.trim();
        let fieldValid = true;

        if (!val) { fieldValid = false; }
        else if (type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val)) { fieldValid = false; }
        else if (min && val.length < min) { fieldValid = false; }

        if (!fieldValid) {
          input.classList.add('error');
          error.textContent = msg;
          error.classList.add('visible');
          valid = false;
        }
      });

      if (valid) {
        const success = document.getElementById('formSuccess');
        const submit  = form.querySelector('button[type="submit"]');
        if (submit) {
          submit.textContent = 'Sending…';
          submit.disabled = true;
        }
        setTimeout(() => {
          if (success) success.classList.add('visible');
          form.reset();
          if (submit) { submit.textContent = 'Send Message'; submit.disabled = false; }
        }, 1200);
      }
    });

    // Live validation clear on input
    form.querySelectorAll('.form-control').forEach(input => {
      input.addEventListener('input', () => {
        input.classList.remove('error');
        const err = document.getElementById(input.id + 'Error');
        if (err) err.classList.remove('visible');
      });
    });
  }

  /* ─── Smooth scroll for anchor links ─────────────────────── */
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', (e) => {
      const target = document.querySelector(anchor.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  /* ─── Blog filter (blogs page) ───────────────────────────── */
  const filterBtns = document.querySelectorAll('.blog-filter-btn');
  const blogCards  = document.querySelectorAll('.blog-card[data-category]');

  if (filterBtns.length) {
    filterBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        filterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const cat = btn.dataset.filter;
        blogCards.forEach(card => {
          const match = cat === 'all' || card.dataset.category === cat;
          card.style.display = match ? '' : 'none';
        });
      });
    });
  }

  /* ─── Animated counter (technology page) ────────────────── */
  const counters = document.querySelectorAll('[data-count]');
  if (counters.length) {
    const countObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const el  = entry.target;
          const end = parseInt(el.dataset.count, 10);
          let cur = 0;
          const step = Math.ceil(end / 60);
          const tick = setInterval(() => {
            cur = Math.min(cur + step, end);
            el.textContent = cur + (el.dataset.suffix || '');
            if (cur >= end) clearInterval(tick);
          }, 16);
          countObserver.unobserve(el);
        }
      });
    }, { threshold: 0.5 });
    counters.forEach(c => countObserver.observe(c));
  }

});