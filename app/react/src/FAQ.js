import React, {Component} from 'react';

class FAQ extends Component {
  constructor(props) {
    super(props);
  }
  componentDidMount() {
     window.scrollTo(0,0)
  }
  render () {
    return (
	     <div>
          <h1 style={{fontSize: "24px", paddingTop:"25px"}}>Frequently Asked Questions (FAQ)</h1>
          <br/>
       		<ul>
            <b>What is the procedure to install this app{`?`}</b>
         		<p>Go to the Social Proof Samurai <a href="https://apps.shopify.com/social-proof-samurai">app listing page</a>. Click the installation button labelled "Get". After approving the permissions that the app requires, you will be redirected to the Social Proof Samurai settings page. We set the default social proof settings for you, but feel free to edit them to best suit your needs.</p>
            <br/>
         		<b>When will my social proof data get refreshed{`?`}</b>
         		<p>We scan your orders database every few hours in order to make sure the social proof data on your products is as up to date as possible.</p>
            <br/>
         		<b>No pop up is showing on my product pages</b>
         		<p>The furthest Social Proof Samurai will check orders is within the last 7 days. If a product does not have an order within that time, then no pop up will appear.</p>
            <br/>
         		<p>If you had an order within the last 7 days or within your specific look back period and its not showing up, then your theme files may be preventing it from popping up. Please follow the manual installation instructions <a href="https://socialproof-samurai.herokuapp.com/installation_guide">here.</a></p>
            <br/>
         		<b>Does the Social Proof Samurai app affect my theme files{`?`}</b>
         		<p>No. This app does not make any changes to your theme/liquid files.</p>
            <br/>
         		<b>How can I contact you for support{`?`}</b>
         		<p>Please contact us at socialproof.samurai@gmail.com. We will get back to you within 24-48 hours.</p>
            <br/>
         		<b> How can I uninstall your app{`?`} </b>
         		<p> Please visit your store’s application page to uninstall Social Proof Samurai.</p>
          </ul>
          <br/>
       		<hr/>
       		<span className="text-muted"><b>Still having trouble{`?`}</b>
            <br/>
             Email us at <a href="mailto:socialproof.samurai@gmail.com?Subject=Help%20request" target="_top">socialproof.samurai@gmail.com</a> for support.
           </span>
  	   </div>
    );
  }
}

export default FAQ;
