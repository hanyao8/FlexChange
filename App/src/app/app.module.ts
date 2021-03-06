import { NgModule, ErrorHandler } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { IonicApp, IonicModule, IonicErrorHandler } from 'ionic-angular';
import { MyApp } from './app.component';

import { ContactPage } from '../pages/contact/contact';
import { HomePage } from '../pages/home/home';
import { TabsPage } from '../pages/tabs/tabs';

import { StatusBar } from '@ionic-native/status-bar';
import { SplashScreen } from '@ionic-native/splash-screen';
import { HTTP_INTERCEPTORS, HttpClientModule } from "@angular/common/http";
import { TokenInterceptor } from "../helpers/token.interceptor";
import { LoginPage } from "../pages/login/login";
import { AuthProvider } from '../providers/auth/auth';
import { WalletPage } from "../pages/wallet/wallet";
import { DepositPage } from "../pages/deposit/deposit";
import { DepositProvider } from '../providers/deposit/deposit';
import { CurrencyProvider } from '../providers/currency/currency';
import { WalletProvider } from '../providers/wallet/wallet';

@NgModule({
  declarations: [
    MyApp,
    ContactPage,
    HomePage,
    TabsPage,
    LoginPage,
    WalletPage,
    DepositPage,
  ],
  imports: [
    BrowserModule,
    IonicModule.forRoot(MyApp),
    HttpClientModule,
  ],
  bootstrap: [IonicApp],
  entryComponents: [
    MyApp,
    ContactPage,
    HomePage,
    TabsPage,
    WalletPage,
    LoginPage,
    DepositPage,
  ],
  providers: [
    StatusBar,
    SplashScreen,
    AuthProvider,
    {provide: ErrorHandler, useClass: IonicErrorHandler},
    {provide: HTTP_INTERCEPTORS, useClass: TokenInterceptor, multi: true},
    WalletProvider,
    DepositProvider,
    CurrencyProvider,
  ]
})
export class AppModule {
}
