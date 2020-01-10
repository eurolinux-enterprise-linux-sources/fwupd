%global glib2_version 2.45.8
%global libappstream_version 0.5.10
%global libgusb_version 0.2.9
%global libsoup_version 2.51.92

%ifarch x86_64 aarch64
%global have_uefi 1
%endif

Summary:   Firmware update daemon
Name:      fwupd
Version:   0.8.2
Release:   3%{?dist}
License:   GPLv2+
URL:       https://github.com/hughsie/fwupd
Source0:   http://people.freedesktop.org/~hughsient/releases/%{name}-%{version}.tar.xz

# already upstream
Patch0:    fwupd-fix-under-including.patch
Patch1:    0001-trivial-Return-a-sensible-error-if-DownloadURI-is-in.patch
Patch2:    0001-Do-not-use-the-LVFS.patch
Patch3:    fwupd-only-use-old-systemd-protections.patch

BuildRequires: docbook-utils
BuildRequires: gettext
BuildRequires: glib2-devel >= %{glib2_version}
BuildRequires: intltool
BuildRequires: libappstream-glib-devel >= %{libappstream_version}
BuildRequires: libgudev1-devel
BuildRequires: libgusb-devel >= %{libgusb_version}
BuildRequires: libsoup-devel >= %{libsoup_version}
BuildRequires: colord-devel >= 1.0.0
BuildRequires: polkit-devel >= 0.103
BuildRequires: libgcab1-devel
BuildRequires: sqlite-devel
BuildRequires: gpgme-devel
BuildRequires: systemd
BuildRequires: libarchive-devel
BuildRequires: gobject-introspection-devel
BuildRequires: gcab
BuildRequires: elfutils-libelf-devel
BuildRequires: gtk-doc

%if 0%{?have_uefi}
BuildRequires: fwupdate-devel >= 7
%endif

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

Requires: glib2%{?_isa} >= %{glib2_version}
Requires: libappstream-glib%{?_isa} >= %{libappstream_version}
Requires: libgusb%{?_isa} >= %{libgusb_version}
Requires: libsoup%{?_isa} >= %{libsoup_version}

Obsoletes: fwupd-sign < 0.1.6
Obsoletes: libebitdo < 0.7.5-3

%description
fwupd is a daemon to allow session software to update device firmware.

%package devel
Summary: Development package for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}
Obsoletes: libebitdo-devel < 0.7.5-3

%description devel
Files for development with %{name}.

%prep
%setup -q
%patch0 -p1 -b .underinclude
%patch1 -p1 -b .sensible-error
%patch2 -p1 -b .no-lvfs
%patch3 -p1 -b .no-new-systemd

%build
%configure \
        --disable-static        \
        --disable-thunderbolt   \
        --enable-gtk-doc        \
        --enable-colorhug       \
%if 0%{?have_uefi}
        --enable-uefi           \
%else
        --disable-uefi          \
%endif
        --disable-dell          \
        --disable-synaptics     \
        --disable-rpath         \
        --disable-silent-rules  \
        --disable-dependency-tracking

make %{?_smp_mflags}

%install
make install DESTDIR=$RPM_BUILD_ROOT
find %{buildroot} -name '*.la' -exec rm -f {} ';'
mkdir --mode=0700 $RPM_BUILD_ROOT%{_localstatedir}/lib/fwupd/gnupg

# not ready yet
rm -f %{buildroot}%{_libdir}/fwupd-plugins-2/libfu_plugin_altos.so
rm -f %{buildroot}%{_libdir}/fwupd-plugins-2/libfu_plugin_raspberrypi.so
rm -f %{buildroot}%{_libdir}/fwupd-plugins-2/libfu_plugin_steelseries.so
rm -f %{buildroot}%{_libdir}/fwupd-plugins-2/libfu_plugin_unifying.so

# we don't want to include this in RHEL yet
rm -rf %{buildroot}%{_datadir}/gtk-doc/html/libdfu
rm -rf %{buildroot}%{_includedir}/libdfu
rm -f %{buildroot}%{_includedir}/dfu.h
rm -f %{buildroot}%{_includedir}/libdfu/*.h
rm -f %{buildroot}%{_libdir}/pkgconfig/dfu.pc

%find_lang %{name}

%check
# make check VERBOSE=1

%post
/sbin/ldconfig
%systemd_post fwupd.service

%preun
%systemd_preun fwupd.service

%postun
/sbin/ldconfig
%systemd_postun_with_restart fwupd.service

%files -f %{name}.lang
%doc README.md AUTHORS NEWS
%license COPYING
%config(noreplace)%{_sysconfdir}/fwupd.conf
%dir %{_libexecdir}/fwupd
%{_libexecdir}/fwupd/fwupd
%{_bindir}/fwupdmgr
%{_sysconfdir}/pki/fwupd
%{_sysconfdir}/pki/fwupd-metadata
%{_sysconfdir}/dbus-1/system.d/org.freedesktop.fwupd.conf
%{_datadir}/app-info/xmls/org.freedesktop.fwupd.xml
%{_datadir}/dbus-1/interfaces/org.freedesktop.fwupd.xml
%{_datadir}/polkit-1/actions/org.freedesktop.fwupd.policy
%{_datadir}/polkit-1/rules.d/org.freedesktop.fwupd.rules
%{_datadir}/dbus-1/system-services/org.freedesktop.fwupd.service
%{_datadir}/man/man1/fwupdmgr.1.gz
%{_unitdir}/fwupd-offline-update.service
%{_unitdir}/fwupd.service
%{_unitdir}/system-update.target.wants/
%dir %{_localstatedir}/lib/fwupd
%{_libdir}/libfwupd*.so.*
%{_libdir}/girepository-1.0/Fwupd-1.0.typelib
/usr/lib/udev/rules.d/*.rules
%dir %{_libdir}/fwupd-plugins-2
%{_libdir}/fwupd-plugins-2/libfu_plugin_colorhug.so
%{_libdir}/fwupd-plugins-2/libfu_plugin_dfu.so
%{_libdir}/fwupd-plugins-2/libfu_plugin_ebitdo.so
%{_libdir}/fwupd-plugins-2/libfu_plugin_test.so
%{_libdir}/fwupd-plugins-2/libfu_plugin_udev.so
%if 0%{?have_uefi}
%{_libdir}/fwupd-plugins-2/libfu_plugin_uefi.so
%endif
%{_libdir}/fwupd-plugins-2/libfu_plugin_upower.so
%{_libdir}/fwupd-plugins-2/libfu_plugin_usb.so
%ghost %{_localstatedir}/lib/fwupd/gnupg

# merged from libdfu upstream
%{_bindir}/dfu-tool
%{_datadir}/man/man1/dfu-tool.1.gz
%{_libdir}/girepository-1.0/Dfu-1.0.typelib
%{_libdir}/libdfu*.so.*

%files devel
%{_datadir}/gir-1.0/Fwupd-1.0.gir
%{_datadir}/gtk-doc/html/libfwupd
%{_includedir}/fwupd-1
%{_libdir}/libfwupd*.so
%{_libdir}/pkgconfig/fwupd.pc

# merged from libdfu upstream
%{_datadir}/gir-1.0/Dfu-1.0.gir
%{_libdir}/libdfu*.so

%changelog
* Mon Jul 03 2017 Richard Hughes <richard@hughsie.com> 0.8.2-3
- Do not use systemd protections not yet available in RHEL.
- Resolves: #1380827

* Mon May 08 2017 Richard Hughes <richard@hughsie.com> 0.8.2-2
- Do not use the LVFS by default.
- Resolves: #1380827

* Thu Apr 20 2017 Richard Hughes <richard@hughsie.com> 0.8.2-1
- Initial upload for RHEL.
- Resolves: #1380827
