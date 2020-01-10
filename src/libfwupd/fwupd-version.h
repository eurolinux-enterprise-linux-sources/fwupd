/* -*- Mode: C; tab-width: 8; indent-tabs-mode: t; c-basic-offset: 8 -*-
 *
 * Copyright (C) 2015 Richard Hughes <richard@hughsie.com>
 *
 * Licensed under the GNU Lesser General Public License Version 2.1
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
 */

/**
 * SECTION:fwupd-version
 * @short_description: Obtains the version for the installed fwupd
 *
 * These compile time macros allow the user to enable parts of client code
 * depending on the version of libfwupd installed.
 */

#if !defined (__FWUPD_H_INSIDE__) && !defined (FWUPD_COMPILATION)
#error "Only <fwupd.h> can be included directly."
#endif

#ifndef __FWUPD_VERSION_H
#define __FWUPD_VERSION_H

/**
 * FWUPD_MAJOR_VERSION:
 *
 * The compile-time major version
 */
#define FWUPD_MAJOR_VERSION				(0)

/**
 * FWUPD_MINOR_VERSION:
 *
 * The compile-time minor version
 */
#define FWUPD_MINOR_VERSION				(8)

/**
 * FWUPD_MICRO_VERSION:
 *
 * The compile-time micro version
 */
#define FWUPD_MICRO_VERSION				(2)

/**
 * FWUPD_CHECK_VERSION:
 * @major: Major version number
 * @minor: Minor version number
 * @micro: Micro version number
 *
 * Check whether a fwupd version equal to or greater than
 * major.minor.micro.
 */
#define FWUPD_CHECK_VERSION(major,minor,micro)    \
    (FWUPD_MAJOR_VERSION > (major) || \
     (FWUPD_MAJOR_VERSION == (major) && FWUPD_MINOR_VERSION > (minor)) || \
     (FWUPD_MAJOR_VERSION == (major) && FWUPD_MINOR_VERSION == (minor) && \
      FWUPD_MICRO_VERSION >= (micro)))

#endif /* __FWUPD_VERSION_H */
