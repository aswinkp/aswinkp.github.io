---
layout:     post
title:      Django with Angular2 Tutorial
date:       2016-08-15 11:21:29
summary:    getting started with Django and Angular2.
categories: django, angular2, tutorial
---

Django is awesome. Angular2 is also awesome. Many forums suggest that they both are awesome when there is abrupt seperation between them.

However need may arise to combine both django and angular2 to make your project double awesome.

I have come across a situation where I need to use angular2 and django side-by-side utilizing the features of both. To make it more complicated, requirement stated that angular application should be in the root url after login. It would have been bit easier if angular app is served from sub folder like domain.com/app/. Anyways, I wanted to find the solution (again, under critical deadline). 

> Donload the source code [HERE](https://github.com/aswinkp/django-ng2-starter).

### Project Setup

```bash
virtualenv /path/to/env/

cd /path/to/env/

source bin/activate

pip install django

django-admin startproject project_name

cd project_name/

python manage.py startapp app_name

python manage.py migrate

mkdir ngApp

cd ngApp

git clone https://github.com/angular/quickstart .

rm -rf .git/ .github/

mv index.html /path/to/django/app/templates/index.html

mv styles.css /path/to/django/app/static/css/styles.css

npm install
```

Now that we have succesfully setup our project directory.

In settings.py file

```python
ANGULAR_URL = '/ng/'

ANGULAR_ROOT = os.path.join(BASE_DIR, 'ngApp/')
```

The above lines do same as static url and static root. Render static files inside ngApp/ directory.

Edit config in `systemjs.config.js`.

```typescript
var config = {
map: map,
baseURL: '/ng/',
packages: packages
};
```

Note that `baseURL: '/ng/'` in the ANGULAR_URL

Now lets add some views in `views.py`.

```python
class AngularApp(TemplateView):
  template_name = 'index.html'

  def get_context_data(self, **kwargs):
  context = super(AngularApp, self).get_context_data(**kwargs)
  context['ANGULAR_URL'] = settings.ANGULAR_URL
  return context

class SampleView(View):
	"""View to render django template to angular"""
	def get(self, request):
	return render("OK!")
```
Note that we are passing `ANGULAR_URL` as the context. This is to avoid hardcoding the path in the template.

Add the below in `urls.py`.
```python
ngurls = [
  url(r'^$', SampleView.as_view(), name='sample'),
]

urlpatterns = [
  url(r'^admin/', admin.site.urls),
  url(r'^(?!ng/).*$', AngularApp.as_view(), name="angular_app"),
] + static(settings.ANGULAR_URL, document_root=settings.ANGULAR_ROOT)
```
Here `(?!ng/)` is the ANGULAR_URL

Remember since you need the angular app in the root URL, you need to accept all the routing except static files in the ngApp. `url(r'^(?!ng/).*$'` does the same. It accepts all the paths except `domain.com/ng/`.
This leaves you another challenge. If you route to domain.com/someurl/ , the above django route will show you to index.html, where you will have angular application. So, you have to handle 404 pages in angular application also. 

Here comes the important part. We are using the django template to call the angular application. This is the place where you can make double awesome. You can add django logics here.

Now create `index.html` in templates folder under django app.

```django{% raw %}
{% load static %}


<html>
  <head>
    <title>Angular 2 QuickStart</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="{% static 'css/styles.css' %}">
    <base href="/">
    <!-- Polyfill(s) for older browsers -->
    <script src="{{ ANGULAR_URL }}node_modules/core-js/client/shim.min.js"></script>
    <script src="{{ ANGULAR_URL }}node_modules/zone.js/dist/zone.js"></script>
    <script src="{{ ANGULAR_URL }}node_modules/reflect-metadata/Reflect.js"></script>
    <script src="{{ ANGULAR_URL }}node_modules/systemjs/dist/system.src.js"></script>
    <script src="{{ ANGULAR_URL }}systemjs.config.js"></script>

    {# -------------------------------------- #}
    {# Write your django logics anywhere here #}
    {# -------------------------------------- #}

    <script>
      window.STATIC_URL = "{{ ANGULAR_URL }}";
      System.import('/ng/app/main').catch(function(err){
          console.error(err);
      });
    </script>
  </head>
  <body>
    <my-app>Loading...</my-app>
  </body>
</html>
```{% endraw %}

In `System.import` you should specify `/ANGULAR_URL/angular_app_folder/name_of_main`.

For example, if you have two angular applications based on user roles, you can set a condition here and route them accordingly by changing in `System.import`. Or you can display the name and profile picture current user in the template or something similar to stackoverfow reputation of current user but remember you  can handle it in angular also. One thing you should keep in mind is that if you are using the above model, keep login and registration as a pure django template.

Now create the following files.

`main.ts`

```typescript
import { bootstrap }    from '@angular/platform-browser-dynamic';

import { AppComponent } from './app.component';
import {appRouterProviders} from "./app.route";
import {HTTP_PROVIDERS} from "@angular/http";
import {enableProdMode} from '@angular/core';

enableProdMode();
bootstrap(AppComponent, [
  appRouterProviders,
  HTTP_PROVIDERS
])
.catch(err => console.error(err));
```


`cd app`

Lets add two more components to implement routing.

`app.route.ts`

```typescript
import { provideRouter, RouterConfig } from '@angular/router';
import {Component1Component} from "./component1.component";
import {Component2Component} from "./component2.component";

const routes: RouterConfig = [
	{ path: '',redirectTo: '/component1',pathMatch: 'full'},
  { path: 'component1', component: Component1Component },
  { path: 'component2', component: Component2Component },
];

export const appRouterProviders = [
  provideRouter(routes)
];
```

`app.component.ts`

```typescript
import { Component } from '@angular/core';
import { ROUTER_DIRECTIVES } from '@angular/router';

@Component({
    selector: 'my-app',
    template: `
        <h1>My First Angular 2 App</h1>
        <nav>
          <a routerLink="/component1" routerLinkActive="active">Component 1</a>
          <a routerLink="/component2" routerLinkActive="active">Component 2</a>
        </nav>
        <router-outlet></router-outlet>
    `,
    directives: [ROUTER_DIRECTIVES]
})
export class AppComponent { }
```

`component1.component.ts`

```typescript
import {Component} from "@angular/core";
@Component({
  template: '<h1>Component 1</h1>'
})
export class Component1Component{

}
```

`component2.component.ts`

```typescript
import {Component} from "@angular/core";
@Component({
  template: '<h1>Component 2</h1>'
})
export class Component2Component{

}
```

Now your folder structure should look something like this. I have included all the files in the tree below.

<pre>
.
├── core
│   ├── admin.py
│   ├── apps.py
│   ├── __init__.py
│   ├── migrations
│   │   ├── __init__.py
│   ├── models.py
│   ├── static
│   │   └── css
│   │       └── styles.css
│   ├── templates
│   │   └── index.html
│   ├── tests.py
│   ├── views.py
├── project
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
├── db.sqlite3
├── LICENSE
├── manage.py
├── ngApp
│   ├── app
│   │   ├── app.component.spec.ts
│   │   ├── app.component.ts
│   │   ├── app.route.ts
│   │   ├── component1.component.ts
│   │   ├── component2.component.ts
│   │   └── main.ts
│   ├── CHANGELOG.md
│   ├── Dockerfile
│   ├── e2e
│   ├── node_modules
│   │   ├
│   ├── README.md
│   ├── typings
│   │   ├── 
└── README.md</pre>

```
cd /path/to/ngApp/

npm start 
```

Open a new terminal,

```
cd path/to/django-ng2-starter/

python manage.py runserver

```

Now visit `localhost:8000` in your browser. You need NPM runing in another terminal during development phase to compile typescript into javascript as you are making changes. 

### Happy Coding :)
___