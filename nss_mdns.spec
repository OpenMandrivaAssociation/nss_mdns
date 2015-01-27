%define rname nss-mdns

%define major 2
%define libname %mklibname %{name} %{major}

Summary:	Multicast dns support for glibc domain resolver
Name:		nss_mdns
Version:	0.10
Release:	26
License:	GPLv2+
Group:		System/Libraries
Url:		http://0pointer.de/lennart/projects/%{rname}/
Source0:	http://0pointer.de/lennart/projects/%{rname}/%{rname}-%{version}.tar.bz2
BuildRequires:	pkgconfig(avahi-core)
Requires(post,postun):	sed
Requires:	%{name}-libraries
Requires:	avahi

%description
nss-mdns is a plugin for the Name Service Switch (NSS) functionality of the
glibc providing host name resolution via Multicast DNS (aka Zeroconf, aka
Apple Rendezvous), effectively allowing name resolution by common
Unix/Linux programs in the ad-hoc mDNS domain .local.

nss-mdns provides client functionality only, which means that you have to run
a mDNS responder daemon separately from nss-mdns if you want to register
the local host name via mDNS.

%files
%doc README doc/README.html doc/style.css
%config(noreplace) %{_sysconfdir}/mdns.allow

%post
if [ $1 = 1 ]; then
    if [ -f /etc/nsswitch.conf ] ; then
	sed -i.bak '
	    /^hosts:/ !b
	    /\<mdns\(4\|6\)\?\(_minimal\)\?\>/ b
	    s/\([[:blank:]]\+\)dns\>/\1mdns4_minimal [NOTFOUND=return] dns/g
	    ' /etc/nsswitch.conf
    fi
fi

%postun
if [ $1 = 0 ]; then
    if [ -f -a /etc/nsswitch.conf ] ; then
	sed -i.bak '
	    /^hosts:/ !b
	    s/[[:blank:]]\+mdns\(4\|6\)\?\(_minimal\( \[NOTFOUND=return\]\)\?\)\?//g
	    ' /etc/nsswitch.conf
    fi
fi

#----------------------------------------------------------------------------

%package -n %{libname}
Summary:	Plugin libraries for nss-mdns
Group:		System/Libraries
Requires:	%{name} = %{EVRD}
Conflicts:	%{name} < 0.10-23
Provides:	%{name}-libraries = %{EVRD}

%description -n %{libname}
Plugin libraries for nss-mdns.

%files -n %{libname}
/%{_lib}/*.so.%{major}

#----------------------------------------------------------------------------

%prep
%setup -qn %{rname}-%{version}

%build
%configure \
	--localstatedir=%{_var}/ \
	--libdir=/%{_lib} \
	--enable-avahi
%make

%install
%makeinstall_std

mkdir -p %{buildroot}%{_sysconfdir}
cat > %{buildroot}%{_sysconfdir}/mdns.allow  <<EOF
# place here the domain that should be resolved by multicast dns
# use * to include all ( not recommended )
.local.
.local
EOF

