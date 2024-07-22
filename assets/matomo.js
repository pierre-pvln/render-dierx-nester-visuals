/*
 *   Script to use in plotly dash to get access data in Matomo
 *
 *   https://stackoverflow.com/questions/53893045/how-to-add-google-analytics-to-plotly-dash-app
 *   It is import to remove the <script> and </script> tags from the auto generated matomo script
 *   
 *   This script is puts in the footer section. 
 *
 *   If script needs to be in header section then
 *   https://community.plotly.com/t/tracking-application-analytics-with-google-analytics/38946/4
 *
 */
<!-- Matomo -->
<!-- <script> -->
  var _paq = window._paq = window._paq || [];
  /* tracker methods like "setCustomDimension" should be called before "trackPageView" */
  _paq.push(['trackPageView']);
  _paq.push(['enableLinkTracking']);
  (function() {
    var u="https://siteanalytics.tst-web.nl/";
    _paq.push(['setTrackerUrl', u+'matomo.php']);
    _paq.push(['setSiteId', '6']);
    var d=document, g=d.createElement('script'), s=d.getElementsByTagName('script')[0];
    g.async=true; g.src=u+'matomo.js'; s.parentNode.insertBefore(g,s);
  })();
<!-- </script> -->
<!-- End Matomo Code -->
