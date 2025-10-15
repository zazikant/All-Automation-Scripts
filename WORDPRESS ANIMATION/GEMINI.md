  This process involves four main stages:
   1. Isolating Your Target: Getting a unique identifier (a CSS ID or Class) for your Elementor container.
   2. Writing the Animation Code: Creating the GSAP JavaScript code for your animation.
   3. Loading the GSAP Library: Using GTM to add the GSAP library to your site.
   4. Deploying the Animation: Using GTM to run your animation code on the correct element and at the correct time.

  ---

  Stage 1: Get the CSS Selector for Your Elementor Container

  For GSAP to animate your container, it needs a unique and stable way to find it. A CSS ID is the best and most reliable way to do this.

   1. Edit with Elementor: Open the page with your container in the Elementor editor.
   2. Select the Container: Click on the container you want to animate.
   3. Go to the Advanced Tab: In the Elementor panel on the left, click the Advanced tab.
   4. Set the CSS ID: In the CSS ID field, give your container a unique, descriptive name. Use lowercase letters and hyphens. For example: hero-animation-container.

  This ID is your target. For this guide, we will use #hero-animation-container as the selector.

  ---

  Stage 2: Write Your GSAP Animation Code

  Next, create the JavaScript code for the animation. Here is a simple example that fades in and slides up the container.

    1 <script>
    2   // Wait for the entire page to load before running the animation
    3   window.addEventListener('load', function() {
    4     // Check if GSAP is available
    5     if (typeof gsap !== 'undefined') {
    6       // Use GSAP to animate the container with the ID 'hero-animation-container'
    7       gsap.fromTo("#hero-animation-container",
    8         {
    9           opacity: 0, // Start with the container invisible
   10           y: 50       // and 50 pixels down
   11         },
   12         {
   13           opacity: 1, // Animate to fully visible
   14           y: 0,       // and its original position
   15           duration: 1.5, // Animation lasts 1.5 seconds
   16           ease: "power2.out" // Use a smooth easing effect
   17         }
   18       );
   19     } else {
   20       console.log("GSAP library not loaded.");
   21     }
   22   });
   23 </script>

----- Below is for CLASS based ----

<script>
  // Wait for the entire page to load before running the animation
  window.addEventListener('load', function() {
    // Check if GSAP is available
    if (typeof gsap !== 'undefined') {
      // Use GSAP to animate all containers with the class 'hero-animation-container'
      // GSAP automatically handles applying the animation to all matched elements.
      gsap.fromTo(".hero-animation-container",
        {
          opacity: 0, // Start with the container invisible
          y: 50       // and 50 pixels down
        },
        {
          opacity: 1, // Animate to fully visible
          y: 0,       // and its original position
          duration: 1.5, // Animation lasts 1.5 seconds
          ease: "power2.out", // Use a smooth easing effect
          stagger: 0.2 // Add a slight delay between each element's animation
        }
      );
    } else {
      console.log("GSAP library not loaded.");
    }
  });
</script>


----- Below is for GSAP SCROLL TRIGGER BASED -- --

<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js"></script>
<script>
// Wait for scripts to load
setTimeout(function() {
  // Check if both GSAP and ScrollTrigger are loaded
  if (typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
    gsap.registerPlugin(ScrollTrigger);
    
    console.log("GSAP and ScrollTrigger loaded successfully");
    
    // Set initial state for all containers (important!)
    gsap.set(".hero-animation-container", {
      opacity: 0,
      y: 50
    });
    
    // Animate each container individually
    gsap.utils.toArray(".hero-animation-container").forEach(function(container, index) {
      console.log("Setting up animation for container:", index);
      
      gsap.to(container, {
        opacity: 1,
        y: 0,
        duration: 1.5,
        ease: "power2.out",
        scrollTrigger: {
          trigger: container,
          start: "top 85%",
          end: "bottom 15%",
          toggleActions: "play none none reverse",
          markers: true, // Shows debug markers - remove in production
          onEnter: function() {
            console.log("Animation triggered for container:", index);
          }
        }
      });
    });
  } else {
    console.log("GSAP or ScrollTrigger not loaded properly");
  }
}, 500); // Increased timeout
</script>

----------------


----_ Text Animation_ -----

<script>
(function() {
  function initAnimation() {
    if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') {
      setTimeout(initAnimation, 200);
      return;
    }
    
    gsap.registerPlugin(ScrollTrigger);
    
    // CSS that forces spans to inherit Elementor heading styles
    var styles = '<style id="elementor-word-animation-fix">' +
      '.google-reveal-text {' +
        'overflow: hidden !important;' +
      '}' +
      
      /* Force spans inside Elementor headings to inherit all typography */ +
      '.elementor-widget-heading .google-reveal-text .word-item,' +
      '.elementor-heading-title .word-item,' +
      '.elementor-widget-heading .word-item {' +
        'font-family: inherit !important;' +
        'font-size: inherit !important;' +
        'font-weight: inherit !important;' +
        'font-style: inherit !important;' +
        'line-height: inherit !important;' +
        'letter-spacing: inherit !important;' +
        'text-transform: inherit !important;' +
        'color: inherit !important;' +
        'text-decoration: inherit !important;' +
        'display: inline-block;' +
        'transform: translateY(100%);' +
        'opacity: 0;' +
      '}' +
      
      /* Also target common Elementor text elements */ +
      '.elementor-widget-text-editor .google-reveal-text .word-item,' +
      '.elementor-text-editor .word-item {' +
        'font-family: inherit !important;' +
        'font-size: inherit !important;' +
        'font-weight: inherit !important;' +
        'font-style: inherit !important;' +
        'line-height: inherit !important;' +
        'letter-spacing: inherit !important;' +
        'text-transform: inherit !important;' +
        'color: inherit !important;' +
        'text-decoration: inherit !important;' +
        'display: inline-block;' +
        'transform: translateY(100%);' +
        'opacity: 0;' +
      '}' +
      
      /* Generic fallback for any other case */ +
      '.google-reveal-text .word-item {' +
        'display: inline-block;' +
        'transform: translateY(100%);' +
        'opacity: 0;' +
      '}' +
      '</style>';
    
    if (!document.querySelector('#elementor-word-animation-fix')) {
      document.head.insertAdjacentHTML('beforeend', styles);
    }
    
    function wrapForAnimation() {
      var elements = document.querySelectorAll('.google-reveal-text:not(.animation-ready)');
      
      for (var i = 0; i < elements.length; i++) {
        var element = elements[i];
        
        // For Elementor, look specifically for the heading title element
        var textElement = element.querySelector('.elementor-heading-title');
        
        // Fallback to other common text elements
        if (!textElement) {
          textElement = element.querySelector('h1, h2, h3, h4, h5, h6, p, span, div');
        }
        
        // Last resort - use the element itself
        if (!textElement) {
          textElement = element;
        }
        
        var textContent = textElement.textContent.trim();
        
        if (textContent) {
          var words = textContent.split(' ');
          var wordElements = [];
          
          for (var w = 0; w < words.length; w++) {
            if (words[w].trim()) {
              wordElements.push('<span class="word-item">' + words[w] + '</span>');
            }
          }
          
          textElement.innerHTML = wordElements.join(' ');
          element.classList.add('animation-ready');
        }
      }
      
      return elements.length;
    }
    
    function setupAnimations() {
      // Handle grouped animations
      var groups = document.querySelectorAll('.google-text-animation');
      
      for (var g = 0; g < groups.length; g++) {
        var container = groups[g];
        var words = container.querySelectorAll('.google-reveal-text.animation-ready .word-item');
        
        if (words.length > 0) {
          var tl = gsap.timeline({
            scrollTrigger: {
              trigger: container,
              start: "top 80%",
              toggleActions: "play none none reverse"
            }
          });
          
          for (var w = 0; w < words.length; w++) {
            var word = words[w];
            var parentElement = word.closest('.google-reveal-text');
            parentElement.classList.add('animation-set');
            
            tl.to(word, {
              y: 0,
              opacity: 1,
              duration: 0.6,
              ease: "power3.out"
            }, w * 0.08);
          }
        }
      }
      
      // Handle individual animations
      var individualContainers = document.querySelectorAll('.google-reveal-text.animation-ready:not(.animation-set)');
      
      for (var j = 0; j < individualContainers.length; j++) {
        var container = individualContainers[j];
        var words = container.querySelectorAll('.word-item');
        
        if (words.length > 0) {
          var tl = gsap.timeline({
            scrollTrigger: {
              trigger: container,
              start: "top 80%",
              toggleActions: "play none none reverse"
            }
          });
          
          for (var k = 0; k < words.length; k++) {
            var word = words[k];
            
            tl.to(word, {
              y: 0,
              opacity: 1,
              duration: 0.6,
              ease: "power3.out"
            }, k * 0.08);
          }
          
          container.classList.add('animation-set');
        }
      }
    }
    
    function init() {
      wrapForAnimation();
      setupAnimations();
    }
    
    init();
    
    var observer = new MutationObserver(function(mutations) {
      var shouldReinit = false;
      
      for (var m = 0; m < mutations.length; m++) {
        var mutation = mutations[m];
        for (var n = 0; n < mutation.addedNodes.length; n++) {
          var node = mutation.addedNodes[n];
          if (node.nodeType === 1) {
            var hasClass = false;
            if (node.classList && node.classList.contains('google-reveal-text')) {
              hasClass = true;
            }
            if (node.querySelector && node.querySelector('.google-reveal-text')) {
              hasClass = true;
            }
            if (hasClass) {
              shouldReinit = true;
            }
          }
        }
      }
      
      if (shouldReinit) {
        setTimeout(init, 100);
      }
    });
    
    observer.observe(document.body, { 
      childList: true, 
      subtree: true 
    });
  }
  
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      setTimeout(initAnimation, 500);
    });
  } else {
    setTimeout(initAnimation, 500);
  }
})();
</script>

🔧 Usage Remains Same:

Just add google-reveal-text class in Elementor
Works with single words or long sentences
For multiple lines, use google-text-animation container

---------



  This code does the following:
   * Waits for the page to fully load (window.addEventListener('load', ...)).
   * Selects your container using its ID (#hero-animation-container).
   * Animates it from a state of being invisible and slightly offset (opacity: 0, y: 50) to its final state (opacity: 1, y: 0).

  ---

  Stage 3: Create the Tags in Google Tag Manager

  You will create two tags in GTM:
   1. GSAP Library Tag: To load the main GSAP library from a CDN.
   2. GSAP Animation Tag: To run the animation code you wrote above.

  Tag 1: Load the GSAP Library

   1. New Tag: In your GTM workspace, go to Tags and click New.
   2. Name the Tag: Name it something clear, like Library - GSAP Core.
   3. Tag Configuration:
       * Click Tag Configuration and choose Custom HTML.
       * Paste the following code into the HTML box. This loads the GSAP library from a trusted CDN.

   1         <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
   4. Triggering:
       * Click Triggering and choose the DOM Ready trigger. If you don't have one, you can create a new trigger of type "DOM Ready".
   5. Save the tag.

  Tag 2: Deploy the Animation Code

   1. New Tag: Create another new tag.
   2. Name the Tag: Name it something like Animation - Hero Container Fade In.
   3. Tag Configuration:
       * Click Tag Configuration and choose Custom HTML.
       * Paste the animation code from Stage 2 into the HTML box.
   4. Advanced Settings: Tag Sequencing
       * This is a critical step. The animation code must not run before the GSAP library is loaded.
       * Expand the Advanced Settings.
       * Check the box for Fire a tag before `Animation - Hero Container Fade In` fires.
       * In the Setup Tag dropdown, select your Library - GSAP Core tag.
       * This ensures GTM loads the library first, then runs your animation.

   5. Triggering:
       * Click Triggering and, just like before, choose the DOM Ready trigger.
   6. Save the tag.

  ---

  Stage 4: Preview and Publish

   1. Preview: Click the Preview button in the top right of your GTM workspace. Enter your website's URL and connect.
   2. Test: Your site will open in a new tab with the GTM debug console. Navigate to the page with your Elementor container. You should see the animation run. In the debug console, you should see that both your Library - GSAP Core and Animation - Hero Container Fade In tags have
      "Succeeded".
   3. Publish: If everything works as expected, go back to your GTM workspace, click Submit, give your version a name (e.g., "Added GSAP Hero Animation"), and click Publish.

  Your animation is now live on your website.