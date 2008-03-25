%define real_name nss-mdns 

Summary:	Multicast dns support for glibc domain resolver  
Name:		nss_mdns
Version:	0.10
Release:	%mkrel 3
Source:		http://0pointer.de/lennart/projects/%real_name/%real_name-%version.tar.bz2
Group:		System/Libraries
License:	GPL
BuildRequires:	libavahi-core-devel 
Buildroot:	%{_tmppath}/%{name}-%{version}-buildroot
Url:		http://0pointer.de/lennart/projects/%real_name/
# for /etc/sysconfig/network
Requires(post): initscripts

%description
nss-mdns is a plugin for the Name Service Switch (NSS) functionality of the 
glibc providing host name resolution via Multicast DNS (aka Zeroconf, aka 
Apple Rendezvous), effectively allowing name resolution by common 
Unix/Linux programs in the ad-hoc mDNS domain .local.

nss-mdns provides client functionality only, which means that you have to run 
a mDNS responder daemon separately from nss-mdns if you want to register 
the local host name via mDNS.

%prep
%setup -q -n %real_name-%version

%build
%configure --localstatedir=/var/ --libdir=/%_lib --enable-avahi
%make

%install
rm -rf %{buildroot}
%makeinstall
mv $RPM_BUILD_ROOT/%_libdir/ $RPM_BUILD_ROOT/%_lib

mkdir -p $RPM_BUILD_ROOT/%_sysconfdir/
cat > $RPM_BUILD_ROOT/%_sysconfdir/mdns.allow  <<EOF
# place here the domain that should be resolved by multicast dns
# use * to include all ( not recommended )
.local.
.local
EOF


%files
%defattr(-,root,root,755)
%doc README doc/README.html doc/style.css
/%_lib/*
%config(noreplace) %_sysconfdir/mdns.allow

%post 
/sbin/ldconfig

if [ $1 = 1 ]; then
   # ipv4 by default, as explained on the webpage
    source /etc/sysconfig/network
    if [ "${NETWORKING_IPV6}" = "yes" ]; then 
        # for both ipv6 and ipv4
        perl -pi -e '!/mdns/ && s/^(hosts:\s*)([^#]*)(#?.*)$/$1 mdns_minimal $2 mdns $3/' /etc/nsswitch.conf
    else
        perl -pi -e '!/mdns/ && s/^(hosts:\s*)([^#]*)(#?.*)$/$1 mdns4_minimal $2 mdns4 $3/' /etc/nsswitch.conf
    fi
fi

%postun 
/sbin/ldconfig
if [ $1 = 0 ]; then
    perl -pi -e 's/^(hosts:.*)\smdns_minimal\d?(\s.*)$/$1 $2/' /etc/nsswitch.conf
    perl -pi -e 's/^(hosts:.*)\smdns\d?(\s.*)$/$1 $2/' /etc/nsswitch.conf
fi

%clean
rm -rf %{buildroot}
