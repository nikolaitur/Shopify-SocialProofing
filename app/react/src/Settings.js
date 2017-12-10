import React, {Component} from 'react';
import convert from 'color-convert';
import {
  Layout,
  Page,
  FooterHelp,
  Card,
  Link,
  Button,
  FormLayout,
  TextField,
  AccountConnection,
  ChoiceList,
  SettingToggle,
  ColorPicker
} from '@shopify/polaris';

class Settings extends Component {
  constructor(props) {
    super(props);
    this.state = {
      socialSetting: '',
      socialTime: '',
      socialScope: '',
      location: ''
    };
    this.appUrl = context.appUrl;
    this.shop = context.shop;
    this.handleSocialSetting = this.handleSocialSetting.bind(this);
    this.handleTime = this.handleTime.bind(this);
    this.handleClick = this.handleClick.bind(this);
    this.handleSocialScope = this.handleSocialScope.bind(this);
    this.handleLocation = this.handleLocation.bind(this);
  }

  componentWillMount () {
    fetch(this.appUrl + '/api/store_settings/' + this.shop)
    .then((response) => {
        return response.json();
    }).then((data) => {
        console.log(data);
        var f_time = this.convertSocialTimeFromHours(data.look_back);
        this.setState({socialTime: [f_time]});

        this.setState({location: [data.location]});
        this.setState({socialSetting: [data.social_setting]});
        this.setState({socialScope: [data.social_scope]});

        return data;
    }).catch((e) => {
        console.log('error' + e);
    });
  }

  handleSocialSetting (socialSetting) {
    this.setState({socialSetting: socialSetting})
  }

  handleTime (time) {
    this.setState({socialTime: time})
  }

  handleSocialScope (socialScope) {
    this.setState({socialScope: socialScope})
  }

  handleLocation (location) {
    this.setState({location: location})
  }

  convertSocialTimeFromHours(time) {
    // Receive hours and convert to corresponding choice list value, e.g. 24 -> '1d'

    let f_time;
    switch (time) {
          case 1:
            f_time = "1h";
            break;
          case 12:
            f_time = "12h";
            break;
          case 24:
            f_time = "1d";
            break;
          case 168:
            f_time = "7d";
            break;
          default:
            f_time = "1d";
     }
     return f_time
  }

   convertSocialTimeToHours(time) {
    // Receive choice list value and convert to hours, e.g. '1d' -> 24

    let f_time;
    switch (time[0]) {
          case "1h":
            f_time = 1;
            break;
          case "12h":
            f_time = 12;
            break;
          case "1d":
            f_time = 24;
            break;
          case "7d":
            f_time = 168;
            break;
          default:
            f_time = 24;
     }
     return f_time
  }

  handleClick () {

    let postBodyStr = '';
    postBodyStr += 'look_back=';
    postBodyStr += this.convertSocialTimeToHours(this.state.socialTime);
    postBodyStr += '&';

    postBodyStr += 'social_setting=';
    postBodyStr += this.state.socialSetting;
    postBodyStr += '&';

    postBodyStr += 'social_scope=';
    postBodyStr += this.state.socialScope;
    postBodyStr += '&';

    postBodyStr += 'location=';
    postBodyStr += this.state.location;
    postBodyStr += '&';

    console.log(postBodyStr);

    fetch(this.appUrl + '/api/store_settings/' + this.shop, {
        method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          },
          body: postBodyStr
        })
  }

  render() {
    const colorBoxStyle = {
      margin: '5px',
      float: 'right',
      border: '1px solid',
    }

    return (
      <Page
        title="Setup"
      >
        <Layout>
          <Layout.AnnotatedSection
            title="Style"
            description="Customize the appearance and location of the modal"
          >
            <SettingToggle>
              <ChoiceList
                title="Location"
                choices={[
                  {
                    label: 'Lower left',
                    value: 'lower-left'
                  },
                  {
                    label: 'Lower right',
                    value: 'lower-right'
                  }
                ]}
                selected={this.state.location}
                onChange={this.handleLocation}
              />
            </SettingToggle>
          </Layout.AnnotatedSection>
          <Layout.AnnotatedSection
            title="Modal Preview"
            description="This is how your modal will display."
          >
          <Card sectioned>
          Preview of how your modal will look.
          <div style={colorBoxStyle}>
            This is the preview box.
          </div>
          </Card>
          </Layout.AnnotatedSection>
          <Layout.AnnotatedSection
            title="Social Proof Settings"
            description="Display data as number of customers who have added this product, viewed the product,
            or display the last customer who purchased it."
          >
          <Card sectioned>
            <FormLayout>
              <FormLayout.Group>
                <ChoiceList
                  title="Social Proof Setting"
                  choices={[
                    {
                      label: 'Display latest customer to purchase product',
                      value: 'latest'
                    },
                    {
                      label: 'Display number of customers who have purchased product',
                      value: 'purchase'
                    }
                  ]}
                  selected={this.state.socialSetting}
                  onChange={this.handleSocialSetting}
                />
                <ChoiceList
                  title="Look Back Setting"
                  choices={[
                    {
                      label: 'Last hour',
                      value: '1h'
                    },
                    {
                      label: 'Last 12 hours',
                      value: '12h'
                    },
                    {
                      label: 'Last day',
                      value: '1d'
                    },
                    {
                      label: '7 days (Recently)',
                      value: '7d'
                    },
                  ]}
                  selected={this.state.socialTime}
                  onChange={this.handleTime}
                />
              </FormLayout.Group>

            </FormLayout>
          </Card>
          <Card sectioned>
            <FormLayout>
              <FormLayout.Group>
                <ChoiceList
                  title="Scope Setting"
                  choices={[
                    {
                      label: 'Same Product',
                      value: 'product'
                    },
                    {
                      label: 'Vendor',
                      value: 'vendor'
                    },
                    {
                      label: 'Tags',
                      value: 'tags'
                    },
                    {
                      label: 'Collections',
                      value: 'collections'
                    },
                    {
                      label: 'Product Type',
                      value: 'product_type'
                    },
                    {
                      label: 'Any (randomly selected)',
                      value: 'any'
                    },
                  ]}
                  selected={this.state.socialScope}
                  onChange={this.handleSocialScope}
                />
              </FormLayout.Group>

            </FormLayout>
          </Card>
          </Layout.AnnotatedSection>

          <Layout.Section>
          <Button onClick={this.handleClick} primary>Submit & Save</Button>
          </Layout.Section>

          <Layout.Section>
            <FooterHelp>For help visit <Link url="https://www.google.com/search?ei=jLUIWvK0JojimAHg-KY4&q=help&oq=help&gs_l=psy-ab.3..0i67k1l2j0j0i67k1j0j0i67k1j0l4.1185.1507.0.1749.4.4.0.0.0.0.194.194.0j1.1.0....0...1.1.64.psy-ab..3.1.194....0.HDVDjU-AKiQ">styleguide</Link>.</FooterHelp>
          </Layout.Section>
        </Layout>
      </Page>
    );
  }
}

export default Settings;
