%define rname nss-mdns

%define major 2
%define libname %mklibname %{name} %{major}

Summary:	Multicast dns support for glibc domain resolver
Name:		nss_mdns
Version:	0.10
Release:	24
License:	GPLv2+
Group:		System/Libraries
Url:		http://0pointer.de/lennart/projects/%{rname}/
Source0:	http://0pointer.de/lennart/projects/%{rname}/%{rname}-%{version}.tar.bz2
BuildRequires:	pkgconfig(avahi-core)
# for /etc/sysconfig/network
Requires(post):	initscripts
Requires:	%{name}-libraries

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
   # ipv4 by default, as explained on the webpage
    [ -f %{_sysconfdir}/sysconfig/network ] && source %{_sysconfdir}/sysconfig/network
    if [ "${NETWORKING_IPV6}" = "yes" ]; then
        # for both ipv6 and ipv4
        perl -pi -e '!/mdns/ && s/^(hosts:\s*)([^#\n]*)(#?.*)$/$1 mdns_minimal $2 mdns $3/' %{_sysconfdir}/nsswitch.conf
    else
        perl -pi -e '!/mdns/ && s/^(hosts:\s*)([^#\n]*)(#?.*)$/$1 mdns4_minimal $2 mdns4 $3/' %{_sysconfdir}/nsswitch.conf
    fi
fi

%postun
if [ $1 = 0 ]; then
    perl -pi -e 's/^(hosts:.*)\smdns_minimal\d?(\s.*)$/$1 $2/' %{_sysconfdir}/nsswitch.conf
    perl -pi -e 's/^(hosts:.*)\smdns\d?(\s.*)$/$1 $2/' %{_sysconfdir}/nsswitch.conf
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
%configure2_5x \
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

