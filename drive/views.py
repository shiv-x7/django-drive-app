from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import DriveFile,DriveFolder
from django.http import FileResponse,Http404
from django.views.decorators.http import require_POST
from django.db.models import Sum

# Create your views here.

@login_required
def dashboard_view(request):
    # Search query
    query = request.GET.get("q", "").strip()

    # All folders belonging to the logged-in user
    folders = DriveFolder.objects.filter(user=request.user)

    # Search files across Root and all folders
    if query:
        files = DriveFile.objects.filter(
            user=request.user,
            original_name__icontains=query
        ).order_by("-uploaded_at")

        folders = folders.filter(name__icontains=query)

    else:
        # By default, show only Root files
        files = DriveFile.objects.filter(
            user=request.user,
            folder__isnull=True
        ).order_by("-uploaded_at")

    # Calculate storage across all user files
    all_user_files = list(
        DriveFile.objects.filter(user=request.user)
    )

    storage_used = sum(
        drive_file.file_size
        for drive_file in all_user_files
    )

    storage_limit = 500 * 1024 * 1024

    storage_remaining = max(
        storage_limit - storage_used, 0
    )

    storage_percentage = min(
        round(storage_used * 100 / storage_limit, 2),
        100
    )

    context = {
        "files": files,
        "folders": folders,
        "query": query,
        "storage_used": storage_used,
        "storage_limit": storage_limit,
        "storage_remaining": storage_remaining,
        "storage_percentage": storage_percentage,
        "total_files": len(all_user_files),
        "total_folders": DriveFolder.objects.filter(
            user=request.user
        ).count(),
    }

    return render(
        request,
        "drive/dashboard.html",
        context
    )
@login_required
def folder_detail_view(request, folder_id):
    folder = get_object_or_404(
        DriveFolder,
        id=folder_id,
        user=request.user
    )

    files = DriveFile.objects.filter(
        user=request.user,
        folder=folder
    ).order_by("-uploaded_at")

    other_folders = DriveFolder.objects.filter(
        user=request.user
    ).exclude(id=folder.id)

    return render(
        request,
        "drive/folder_detail.html",
        {
            "folder": folder,
            "files": files,
            "other_folders": other_folders,
        }
    )
@login_required
def upload_file_view(request):
    if request.method != "POST":
        return redirect("drive:dashboard")

    uploaded_file = request.FILES.get("file")

    if not uploaded_file:
        messages.error(request, "Please select a file.")
        return redirect("drive:dashboard")

    # Individual file limit: 25 MiB
    max_file_size = 25 * 1024 * 1024

    if uploaded_file.size > max_file_size:
        messages.error(
            request,
            "File size cannot exceed 25 MiB."
        )

        folder_id = request.POST.get("folder_id")
        if folder_id:
            return redirect(
                "drive:folder_detail",
                folder_id=folder_id
            )

        return redirect("drive:dashboard")

    # Total storage limit: 500 MiB per user
    storage_limit = 500 * 1024 * 1024

    # Calculate the user's existing storage usage
    existing_files = DriveFile.objects.filter(
        user=request.user
    )

    storage_used = sum(
        drive_file.file_size
        for drive_file in existing_files
    )

    # Check whether enough storage is available
    if storage_used + uploaded_file.size > storage_limit:
        messages.error(
            request,
            "Storage limit exceeded! Please delete some files "
            "to upload new files."
        )

        folder_id = request.POST.get("folder_id")
        if folder_id:
            return redirect(
                "drive:folder_detail",
                folder_id=folder_id
            )

        return redirect("drive:dashboard")

    # Validate destination folder
    folder = None
    folder_id = request.POST.get("folder_id")

    if folder_id:
        folder = get_object_or_404(
            DriveFolder,
            id=folder_id,
            user=request.user
        )

    # Save the file
    DriveFile.objects.create(
        user=request.user,
        folder=folder,
        file=uploaded_file,
        original_name=uploaded_file.name
    )

    messages.success(
        request,
        "File uploaded successfully!"
    )

    if folder:
        return redirect(
            "drive:folder_detail",
            folder_id=folder.id
        )

    return redirect("drive:dashboard")


@login_required
def view_file(request, file_id):
    drive_file = get_object_or_404(
        DriveFile,
        id=file_id,
        user=request.user
    )

    if not drive_file.file:
        raise Http404("File not found.")

    extension = drive_file.extension

    # File types that can be previewed in the browser
    preview_extensions = [
        ".jpg", ".jpeg", ".png", ".gif", ".webp",
        ".pdf", ".txt"
    ]

    # Open supported files in the browser
    if extension in preview_extensions:
        return FileResponse(
            drive_file.file.open("rb"),
            as_attachment=False,
            filename=drive_file.original_name
        )

    # Other file types will be downloaded
    return FileResponse(
        drive_file.file.open("rb"),
        as_attachment=True,
        filename=drive_file.original_name
    )


@login_required
def download_file(request, file_id):
    drive_file = get_object_or_404(
        DriveFile,
        id=file_id,
        user=request.user
    )

    if not drive_file.file:
        raise Http404("File not found.")

    return FileResponse(
        drive_file.file.open("rb"),
        as_attachment=True,
        filename=drive_file.original_name
    )

@login_required
@require_POST
def delete_file_view(request, file_id):
    drive_file = get_object_or_404(
        DriveFile,
        id=file_id,
        user=request.user
    )

    # Delete the physical file from media storage
    drive_file.file.delete(save=False)

    # Delete the database record
    drive_file.delete()

    messages.success(
        request,
        f"'{drive_file.original_name}' deleted successfully!"
    )

    return redirect("drive:dashboard")

@login_required
@require_POST
def create_folder_view(request):
    folder_name = request.POST.get("folder_name", "").strip()

    if not folder_name:
        messages.error(request, "Folder name cannot be empty.")
        return redirect("drive:dashboard")

    if len(folder_name) > 100:
        messages.error(
            request,
            "Folder name cannot exceed 100 characters."
        )
        return redirect("drive:dashboard")

    # Check whether a folder with this name already exists
    folder_exists = DriveFolder.objects.filter(
        user=request.user,
        name__iexact=folder_name
    ).exists()

    if folder_exists:
        messages.error(
            request,
            "A folder with this name already exists."
        )
        return redirect("drive:dashboard")

    # Create the folder
    DriveFolder.objects.create(
        user=request.user,
        name=folder_name
    )

    messages.success(
        request,
        f"Folder '{folder_name}' created successfully!"
    )

    return redirect("drive:dashboard")


@login_required
@require_POST
def rename_folder_view(request, folder_id):
    folder = get_object_or_404(
        DriveFolder,
        id=folder_id,
        user=request.user
    )

    new_name = request.POST.get("folder_name", "").strip()

    if not new_name:
        messages.error(request, "Folder name cannot be empty.")
        return redirect("drive:dashboard")

    if len(new_name) > 100:
        messages.error(
            request,
            "Folder name cannot exceed 100 characters."
        )
        return redirect("drive:dashboard")

    duplicate = DriveFolder.objects.filter(
        user=request.user,
        name__iexact=new_name
    ).exclude(id=folder.id).exists()

    if duplicate:
        messages.error(
            request,
            "A folder with this name already exists."
        )
        return redirect("drive:dashboard")

    folder.name = new_name
    folder.save(update_fields=["name"])

    messages.success(
        request,
        f"Folder renamed to '{new_name}' successfully!"
    )

    return redirect("drive:dashboard")


@login_required
@require_POST
def delete_folder_view(request, folder_id):
    folder = get_object_or_404(
        DriveFolder,
        id=folder_id,
        user=request.user
    )

    folder_name = folder.name

    # Delete the actual uploaded files from storage first
    for drive_file in folder.files.all():
        drive_file.file.delete(save=False)

    # Delete the folder and its associated database records
    folder.delete()

    messages.success(
        request,
        f"Folder '{folder_name}' deleted successfully!"
    )

    return redirect("drive:dashboard")


@login_required
@require_POST
def move_file_view(request, file_id):

    drive_file = get_object_or_404(
        DriveFile,
        id=file_id,
        user=request.user
    )

    folder_id = request.POST.get("folder_id", "").strip()

    # Move file to Root (My Drive)
    if not folder_id:
        drive_file.folder = None
        drive_file.save(update_fields=["folder"])

        messages.success(
            request,
            f'"{drive_file.original_name}" moved to My Drive (Root).'
        )

        return redirect("drive:dashboard")

    # Move file to another folder
    target_folder = get_object_or_404(
        DriveFolder,
        id=folder_id,
        user=request.user
    )

    drive_file.folder = target_folder
    drive_file.save(update_fields=["folder"])

    messages.success(
        request,
        f'"{drive_file.original_name}" moved to "{target_folder.name}".'
    )

    # Redirect to the source folder if provided
    return_folder_id = request.POST.get("return_folder_id", "").strip()

    if return_folder_id:
        return redirect(
            "drive:folder_detail",
            folder_id=return_folder_id
        )

    return redirect("drive:dashboard")