import { type AppType } from "next/dist/shared/lib/utils";
import Layout from "~/components/Layout";
import "~/styles/globals.css";
import ReactGA from "react-ga4";
import { StrictMode } from 'react';
import { GOOGLE_ANALYTICS_ID, INTERCOM_ID } from "~/constants";
import { IntercomProvider } from "react-use-intercom";

// 只在有 GA ID 时初始化
if (GOOGLE_ANALYTICS_ID) {
  ReactGA.initialize(GOOGLE_ANALYTICS_ID);
}

const MyApp: AppType = ({ Component, pageProps }) => {
  return (
    <StrictMode>
      <IntercomProvider appId={INTERCOM_ID}>
        <Layout>
          <Component {...pageProps} />
        </Layout>
      </IntercomProvider>
    </StrictMode>
  );
};

export default MyApp;
