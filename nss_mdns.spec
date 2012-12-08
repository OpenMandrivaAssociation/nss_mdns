%define real_name nss-mdns

Summary:	Multicast dns support for glibc domain resolver
Name:		nss_mdns
Version:	0.10
Release:	%mkrel 11
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
%configure2_5x --localstatedir=/var/ --libdir=/%_lib --enable-avahi
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
%if %mdkversion < 200900
/sbin/ldconfig
%endif

if [ $1 = 1 ]; then
   # ipv4 by default, as explained on the webpage
    [ -f /etc/sysconfig/network ] && source /etc/sysconfig/network
    if [ "${NETWORKING_IPV6}" = "yes" ]; then
        # for both ipv6 and ipv4
        perl -pi -e '!/mdns/ && s/^(hosts:\s*)([^#\n]*)(#?.*)$/$1 mdns_minimal $2 mdns $3/' /etc/nsswitch.conf
    else
        perl -pi -e '!/mdns/ && s/^(hosts:\s*)([^#\n]*)(#?.*)$/$1 mdns4_minimal $2 mdns4 $3/' /etc/nsswitch.conf
    fi
fi

%postun
%if %mdkversion < 200900
/sbin/ldconfig
%endif
if [ $1 = 0 ]; then
    perl -pi -e 's/^(hosts:.*)\smdns_minimal\d?(\s.*)$/$1 $2/' /etc/nsswitch.conf
    perl -pi -e 's/^(hosts:.*)\smdns\d?(\s.*)$/$1 $2/' /etc/nsswitch.conf
fi

%clean
rm -rf %{buildroot}


%changelog
* Tue Feb 21 2012 abf
- The release updated by ABF

* Wed May 04 2011 Oden Eriksson <oeriksson@mandriva.com> 0.10-10mdv2011.0
+ Revision: 666629
- mass rebuild

* Fri Dec 03 2010 Oden Eriksson <oeriksson@mandriva.com> 0.10-9mdv2011.0
+ Revision: 606829
- rebuild

* Mon Mar 15 2010 Oden Eriksson <oeriksson@mandriva.com> 0.10-8mdv2010.1
+ Revision: 520195
- rebuilt for 2010.1

* Thu Sep 03 2009 Christophe Fergeau <cfergeau@mandriva.com> 0.10-7mdv2010.0
+ Revision: 426258
- rebuild
- use %%configure2_5x instead of %%configure (to avoid calling libtoolize)

* Thu Dec 25 2008 Adam Williamson <awilliamson@mandriva.org> 0.10-6mdv2009.1
+ Revision: 318784
- rebuild for new avahi-core major

* Wed Jul 30 2008 Michael Scherer <misc@mandriva.org> 0.10-5mdv2009.0
+ Revision: 254778
- fix bug 33612, thanks to eric piel for the fix
- remove trailling whitespace in spec

* Tue Jun 17 2008 Thierry Vignaud <tv@mandriva.org> 0.10-4mdv2009.0
+ Revision: 223352
- rebuild

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

  + Michael Scherer <misc@mandriva.org>
    - check that /etc/sysconfig/network existe before source it, reported by muny/yvan
      on irc

* Tue Mar 25 2008 Olivier Blin <oblin@mandriva.com> 0.10-3mdv2008.1
+ Revision: 189917
- require initscripts in post script so that /etc/sysconfig/network is available

* Tue Mar 04 2008 Oden Eriksson <oeriksson@mandriva.com> 0.10-2mdv2008.1
+ Revision: 179098
- rebuild

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Tue May 22 2007 Tomasz Pawel Gajc <tpg@mandriva.org> 0.10-1mdv2008.0
+ Revision: 29702
- new upstream version

  + Michael Scherer <misc@mandriva.org>
    - fix uninstallation scriptlet
    - fix scriptlet to place mdns_minimal before and mdns at the end, related to bug #30340


* Thu Jan 04 2007 Michael Scherer <misc@mandriva.org> 0.9-1mdv2007.0
+ Revision: 104201
- update to 0.9
- Import nss_mdns

