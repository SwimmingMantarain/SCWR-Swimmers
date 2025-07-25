const wrapper    = document.getElementById('header-logo-wrapper');
const staticLogo = document.getElementById('header-logo-static');
const flyLogo    = document.getElementById('header-logo-fly');

wrapper.addEventListener('click', () => {
  // 1) Let HTMX fade out your #content over the first 400ms
  //    and leave the logo sitting there for a moment.

  // compute flight vector
  const rect = staticLogo.getBoundingClientRect();
  const dx   = window.innerWidth  / 2 
             - (rect.left + rect.width  / 2);
  const dy   = window.innerHeight / 2 
             - (rect.top  + rect.height / 2);

  // 2) AFTER content is fully faded (at 400ms), start the fly:
  setTimeout(() => {
    // hide the static one
    staticLogo.style.opacity = 0;

    // prepare the flyer’s transitions
    flyLogo.style.transition = [
      'transform 1.2s ease',   // move+scale
      'opacity 0.6s ease',     // fade‐in then fade‐out
      'border 0.4s ease'       // draw in border at start
    ].join(', ');

    // kick off the “draw border” right away
    flyLogo.style.border = '2px solid #4a90b8';

    // show & animate the flyer into the center at 1.2s
    flyLogo.style.opacity   = 1;
    flyLogo.style.transform = `translate(${dx}px, ${dy}px) scale(1.2)`;

    // 3) halfway through the flight (at 400 ms into this step),
    //    fade the flyer out to leave the blank page moment:
    setTimeout(() => flyLogo.style.opacity = 0, 600);
  }, 400);
});

// 4) Once HTMX has fully settled in your new #content (≈1.6s after click),
//    fade the static logo back, and instantly reset the flyer.
document.body.addEventListener('htmx:afterSettle', () => {
  staticLogo.style.transition = 'opacity 0.4s ease';
  staticLogo.style.opacity    = 1;

  flyLogo.style.transition = 'none';
  flyLogo.style.opacity    = 0;
  flyLogo.style.transform  = 'none';
  flyLogo.style.border     = '0 solid #4a90b8';
});
