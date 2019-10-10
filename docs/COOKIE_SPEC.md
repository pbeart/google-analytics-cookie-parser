# Cookie specification
### This document details how GACP expects GA cookies to be formatted, and therefore how cookie parsing is tested

## _ga cookie

### GA1.2.6542754367.1545651155

#### 1) GA1: Google Analytics version

#### 2) 2: Number of . in the domain

#### 3) 6542754367: Unique visitor identifier

#### 4) 1545651155: First time site visited as UTC Unix epoch timestamp

## __utma cookies

### 58162108.293454173.1545651155.1545651255.1545652355.8

#### 1) 58162108: Hash of cookie domain

#### 2) 293454173: Unique visitor identifier

#### 3) 1545651155: Cookie creation time/first visit as UTC Unix epoch timestamp

#### 4) 1545651255: Second most recent site visit as UTC Unix epoch timestamp

#### 5) 1545652355: Most recent site visit as UTC Unix epoch timestamp

#### 6) 8: Total number of visits

## __utmb cookies

### 58162108.8.7.1545651255

#### 1) 58162108: Hash of cookie domain

#### 2) 8: Page views in current session

#### 3) 7: 10 - number of outbound link clicks, e.g. in this case represents 3 outbound clicks

#### 4) 1545652365: Current session start time as UTC Unix epoch timestamp

## __utmz cookies

### 58162108.1545652355.12.3.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=cute%20puppies

#### 1) 58162108: Hash of cookie domain

#### 2) 1545652355: Most recent site visit as UTC Unix epoch timestamp

#### 3) 12: Number of visits

#### 4) 3: Number of different types/campaigns of visits

#### 5) Key-value pairs of other values:
#### &nbsp;&nbsp;&nbsp;&nbsp; utmcsr: Source of site visit

#### &nbsp;&nbsp;&nbsp;&nbsp; utmccn: AdWords campaign name

#### &nbsp;&nbsp;&nbsp;&nbsp; utmcmd: Access method (organic, referral, cpc (cost per click), email, direct)

#### &nbsp;&nbsp;&nbsp;&nbsp; utmctr: URL-encoded search query to access site 