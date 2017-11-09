import React, {Component} from 'react';
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
} from '@shopify/polaris';

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      first: '',
      last: '',
      email: '',
      checkboxes: [],
      colorSelected: '',
      connected: false,
    };
    this.handleColor = this.handleColor.bind(this)
    this.valueUpdater = this.valueUpdater.bind(this)
  }

  valueUpdater(field) {
    return (value) => this.setState({[field]: value});
  }

  handleColor (color) {
    this.setState({colorSelected: })
  }

  render() {
    const primaryAction = {content: 'New product'};

    return (
      <Page
        title="Settings"
      >
        <Layout>
          <Layout.AnnotatedSection
            title="Style + Appearance"
            description="Customize the appearance of the social proof modal"
          >
          <ColorPicker
            color={{
              hue: 120,
              brightness: 1,
              saturation: 1,
            }}
            alpha
            onChange={this.handleColor}
            />
          </Layout.AnnotatedSection>

         {this.renderAccount()}

          <Layout.AnnotatedSection
            title="Form"
            description="A sample form using Polaris components."
          >
            <Card sectioned>
              <FormLayout>
                <FormLayout.Group>
                  <TextField
                    value={this.state.first}
                    label="First Name"
                    placeholder="Tom"
                    onChange={this.valueUpdater('first')}
                  />
                  <TextField
                    value={this.state.last}
                    label="Last Name"
                    placeholder="Ford"
                    onChange={this.valueUpdater('last')}
                  />
                </FormLayout.Group>

                <TextField
                  value={this.state.email}
                  label="Email"
                  placeholder="example@email.com"
                  onChange={this.valueUpdater('email')}
                />

                <TextField
                  multiline
                  label="How did you hear about us?"
                  placeholder="Website, ads, email, etc."
                  value={this.state.autoGrow}
                  onChange={this.valueUpdater('autoGrow')}
                />

                <ChoiceList
                  allowMultiple
                  choices={choiceListItems}
                  selected={this.state.checkboxes}
                  onChange={this.valueUpdater('checkboxes')}
                />

                <Button primary>Submit</Button>
              </FormLayout>
            </Card>
          </Layout.AnnotatedSection>

          <Layout.Section>
            <FooterHelp>For more details on Polaris, visit our <Link url="https://polaris.shopify.com">styleguide</Link>.</FooterHelp>
          </Layout.Section>

        </Layout>
      </Page>
    );
  }


}

export default App;
