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
      color: {
        hue: '',
        saturation: '',
        brightness: ''
      },
      size: '',
      width: '',
      height: '',
      socialSetting: '',
      socialTime: ''
    };
    this.appUrl = 'http://127.0.0.1:8000';
    this.shop = new URLSearchParams(window.location.search).get('shop');
    this.handleColor = this.handleColor.bind(this);
    this.handleSize = this.handleSize.bind(this);
    this.handleSocial = this.handleSocial.bind(this);
    this.handleTime = this.handleTime.bind(this);
    this.handleClick = this.handleClick.bind(this);
  }

  componentWillMount () {
    fetch(this.appUrl + '/api/store_settings/' + this.shop)
    .then((response) => {
        return response.json();
    }).then((data) => {
        console.log(data);
        var f_time = this.convertSocialTimeFromHours(data.look_back);
        this.setState({socialTime: [f_time]});

        this.setState({socialSetting: [data.social_setting]});
        this.setState({size: [data.size]});
        this.setState({width: [data.size.split(',')[0]]});
        this.setState({height: [data.size.split(',')[1]]});

        this.setState({color: {hue: [data.color_hue], saturation: [data.color_saturation], brightness: [data.color_brightness]}});

        return data;
    }).catch((e) => {
        console.log('error' + e);
    });
  }

  handleColor (color) {
    this.setState({color});
  }

  handleSize (size) {
    this.setState({size})
    let sizeArr = size[0].split(',');
    this.setState({width: sizeArr[0], height: sizeArr[1]});
  }

  handleSocial (social) {
    this.setState({socialSetting: social})
  }

  handleTime (time) {
    this.setState({socialTime: time})
  }

  convertSocialTimeFromHours(time) {
    // Receive hours and convert to corresponding choice list value, e.g. 24 -> '1d'

    let f_time;
    switch (time) {
          case 6:
            f_time = "6h";
            break;
          case 12:
            f_time = "12h";
            break;
          case 24:
            f_time = "1d";
            break;
          case 36:
            f_time = "3d";
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
          case "6h":
            f_time = 6;
            break;
          case "12h":
            f_time = 12;
            break;
          case "1d":
            f_time = 24;
            break;
          case "3d":
            f_time = 36;
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

    postBodyStr += 'color_hue=';
    postBodyStr += this.state.color.hue;
    postBodyStr += '&';

    postBodyStr += 'color_saturation=';
    postBodyStr += this.state.color.saturation;
    postBodyStr += '&';

    postBodyStr += 'color_brightness=';
    postBodyStr += this.state.color.brightness;
    postBodyStr += '&';

    postBodyStr += 'social_setting=';
    postBodyStr += this.state.socialSetting;
    postBodyStr += '&';

    postBodyStr += 'size=';
    postBodyStr += this.state.size;

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
    const { hue, saturation, brightness } = this.state.color;
    const colorBoxStyle = {
      width: `${this.state.width}px`,
      height: `${this.state.height}px`,
      margin: '5px',
      float: 'right',
      border: '1px solid',
      backgroundColor: `hsl(${hue}, ${saturation * 100}%, ${brightness * 100}%)`
    }

    return (
      <Page
        title="Setup"
      >
        <Layout>
          <Layout.AnnotatedSection
            title="Style"
            description="Customize the size and appearance of the modal"
          >
            <SettingToggle>
              <ColorPicker
                color={{
                  hue: this.state.color.hue,
                  brightness: this.state.color.brightness,
                  saturation: this.state.color.saturation
                }}
                onChange={this.handleColor}
              />
            </SettingToggle>
            <SettingToggle>
              <ChoiceList
                title="Dimensions in pixels"
                choices={[
                  {
                    label: '250x100',
                    value: '250,100'
                  },
                  {
                    label: '250x150',
                    value: '250,150'
                  },
                  {
                    label: '300x100',
                    value: '300,100'
                  }
                ]}
                selected={this.state.size}
                onChange={this.handleSize}
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
            description="Display data as # of customers who have added this product, viewed the product,
            or display the last customer who purchased it."
          >
            <Card sectioned>
              <FormLayout>
                <FormLayout.Group>
                  <ChoiceList
                    title="Social Proof Settings (Default: display latest customer)"
                    choices={[
                      {
                        label: '# of customers who have purchased this product',
                        value: 'purchase'
                      },
                      {
                        label: '# of customers who have viewed this product',
                        value: 'view'
                      },
                      {
                        label: 'Display latest customer who purchased this product',
                        value: 'latest'
                      }
                    ]}
                    selected={this.state.socialSetting}
                    onChange={this.handleSocial}
                  />
                  <ChoiceList
                    title="Look Back Duration (Default 1 day)"
                    choices={[
                      {
                        label: 'Last 6 hours',
                        value: '6h'
                      },
                      {
                        label: 'Last 12 hours',
                        value: '12h'
                      },
                      {
                        label: 'Last Day',
                        value: '1d'
                      },
                      {
                        label: 'Last 3 Days',
                        value: '3d'
                      },
                      {
                        label: 'Last 7 Days',
                        value: '7d'
                      },
                    ]}
                    selected={this.state.socialTime}
                    onChange={this.handleTime}
                  />
                </FormLayout.Group>
                <Button onClick={this.handleClick} primary>Submit & Save</Button>
              </FormLayout>
            </Card>
          </Layout.AnnotatedSection>

          <Layout.Section>
            <FooterHelp>For help visit <Link url="https://www.google.com/search?ei=jLUIWvK0JojimAHg-KY4&q=help&oq=help&gs_l=psy-ab.3..0i67k1l2j0j0i67k1j0j0i67k1j0l4.1185.1507.0.1749.4.4.0.0.0.0.194.194.0j1.1.0....0...1.1.64.psy-ab..3.1.194....0.HDVDjU-AKiQ">styleguide</Link>.</FooterHelp>
          </Layout.Section>
        </Layout>
      </Page>
    );
  }
}

export default Settings;
